import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import models
from tqdm import tqdm

from apis_ontology.models import NomanslandMixin


class Command(BaseCommand):
    help = (
        "Scan Nomansland entities for potential token typos and unicode normalization issues, "
        "and export a markdown report including top repeated tokens."
    )

    TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="token_quality_report.md",
            help="Path to markdown report file (default: token_quality_report.md)",
        )
        parser.add_argument(
            "--top-limit",
            type=int,
            default=1000,
            help="How many top tokens to include (default: 1000)",
        )
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=1000,
            help="Iterator chunk size for ORM queries (default: 1000)",
        )
        parser.add_argument(
            "--canonical-min-count",
            type=int,
            default=20,
            help="Minimum frequency to treat a token as a typo correction candidate (default: 20)",
        )
        parser.add_argument(
            "--max-distance",
            type=int,
            default=2,
            help="Maximum Levenshtein distance for typo detection (default: 2)",
        )
        parser.add_argument(
            "--min-token-length",
            type=int,
            default=4,
            help="Minimum token length for typo detection (default: 4)",
        )
        parser.add_argument(
            "--frequency-ratio",
            type=int,
            default=5,
            help=(
                "A typo candidate must be this many times more frequent than its variant "
                "(default: 5)"
            ),
        )
        parser.add_argument(
            "--variant-min-total",
            type=int,
            default=2,
            help=(
                "Minimum total frequency for a diacritic-insensitive token family to "
                "be considered for standardization suggestions (default: 2)"
            ),
        )

    def handle(self, *args, **options):
        output_path = options["output"]
        top_limit = options["top_limit"]
        chunk_size = options["chunk_size"]
        canonical_min_count = options["canonical_min_count"]
        max_distance = options["max_distance"]
        min_token_length = options["min_token_length"]
        frequency_ratio = options["frequency_ratio"]
        variant_min_total = options["variant_min_total"]

        if top_limit <= 0:
            raise ValueError("--top-limit must be greater than 0")
        if chunk_size <= 0:
            raise ValueError("--chunk-size must be greater than 0")
        if canonical_min_count <= 0:
            raise ValueError("--canonical-min-count must be greater than 0")
        if max_distance <= 0:
            raise ValueError("--max-distance must be greater than 0")
        if min_token_length <= 0:
            raise ValueError("--min-token-length must be greater than 0")
        if frequency_ratio <= 1:
            raise ValueError("--frequency-ratio must be greater than 1")
        if variant_min_total <= 1:
            raise ValueError("--variant-min-total must be greater than 1")

        model_field_map = self._collect_models_and_fields()
        if not model_field_map:
            self.stdout.write(self.style.WARNING("No NomanslandMixin concrete models found."))
            return

        self.stdout.write(
            f"Scanning {len(model_field_map)} models to build token frequencies..."
        )
        token_counts, raw_variant_counts, spelling_variant_counts, stats = self._build_token_stats(
            model_field_map, chunk_size=chunk_size
        )

        typo_map = self._build_typo_map(
            token_counts=token_counts,
            max_distance=max_distance,
            min_token_length=min_token_length,
            canonical_min_count=canonical_min_count,
            frequency_ratio=frequency_ratio,
        )
        spelling_standardization_map = self._build_spelling_standardization_map(
            spelling_variant_counts=spelling_variant_counts,
            variant_min_total=variant_min_total,
        )

        self.stdout.write(
            "Collecting per-field potential issues (typos + unicode normalization + spelling variants)..."
        )
        issue_rows = self._collect_issue_rows(
            model_field_map=model_field_map,
            typo_map=typo_map,
            spelling_standardization_map=spelling_standardization_map,
            chunk_size=chunk_size,
        )

        markdown = self._render_markdown_report(
            issue_rows=issue_rows,
            token_counts=token_counts,
            raw_variant_counts=raw_variant_counts,
            stats=stats,
            top_limit=top_limit,
            canonical_min_count=canonical_min_count,
            max_distance=max_distance,
            min_token_length=min_token_length,
            frequency_ratio=frequency_ratio,
            variant_min_total=variant_min_total,
        )

        with open(output_path, "w", encoding="utf-8") as report_file:
            report_file.write(markdown)

        self.stdout.write(
            self.style.SUCCESS(
                f"Token quality report written to {output_path} "
                f"({len(issue_rows)} records with potential issues, {len(token_counts)} unique tokens)."
            )
        )

    def _collect_models_and_fields(self):
        model_field_map = []
        for model in apps.get_models():
            if model._meta.abstract or model._meta.proxy:
                continue
            if not issubclass(model, NomanslandMixin):
                continue

            fields = [
                field.name
                for field in model._meta.get_fields()
                if isinstance(field, (models.CharField, models.TextField))
                and getattr(field, "concrete", False)
            ]
            if not fields:
                continue

            model_field_map.append((model, fields))

        model_field_map.sort(key=lambda item: item[0]._meta.label_lower)
        return model_field_map

    def _build_token_stats(self, model_field_map, chunk_size):
        token_counts = Counter()
        raw_variant_counts = defaultdict(Counter)
        spelling_variant_counts = defaultdict(Counter)
        stats = {
            "records_scanned": 0,
            "non_empty_fields_scanned": 0,
            "models_scanned": len(model_field_map),
        }

        for model, fields in model_field_map:
            queryset = model.objects.only("pk", *fields).iterator(chunk_size=chunk_size)
            record_count = model.objects.count()
            progress = tqdm(
                queryset,
                total=record_count,
                desc=f"Token stats {model.__name__}",
                unit="rec",
            )
            for instance in progress:
                stats["records_scanned"] += 1
                for field_name in fields:
                    value = getattr(instance, field_name, None)
                    if not isinstance(value, str) or not value.strip():
                        continue
                    stats["non_empty_fields_scanned"] += 1
                    for raw_token in self._tokenize(value):
                        normalized_token = self._normalize_token(raw_token)
                        if not normalized_token:
                            continue
                        token_counts[normalized_token] += 1
                        raw_variant_counts[normalized_token][raw_token] += 1
                        spelling_key = self._spelling_key(normalized_token)
                        if spelling_key:
                            spelling_variant_counts[spelling_key][raw_token] += 1

        return token_counts, raw_variant_counts, spelling_variant_counts, stats

    def _build_spelling_standardization_map(self, spelling_variant_counts, variant_min_total):
        standardization_map = {}

        for spelling_key, variants in spelling_variant_counts.items():
            total = sum(variants.values())
            if total < variant_min_total:
                continue

            # Ignore families that differ only by letter case.
            casefolded_forms = {variant.casefold() for variant in variants}
            if len(casefolded_forms) < 2:
                continue

            ordered = variants.most_common()
            preferred = ordered[0][0]
            variant_labels = [f"{variant} ({count})" for variant, count in ordered]

            standardization_map[spelling_key] = {
                "preferred": preferred,
                "variants": variant_labels,
                "total": total,
            }

        return standardization_map

    def _build_typo_map(
        self,
        token_counts,
        max_distance,
        min_token_length,
        canonical_min_count,
        frequency_ratio,
    ):
        canonical_tokens = [
            token for token, count in token_counts.items() if count >= canonical_min_count
        ]

        candidate_index = defaultdict(list)
        for token in canonical_tokens:
            if not token:
                continue
            candidate_index[(token[0], len(token))].append(token)

        typo_map = {}
        for token, token_count in token_counts.items():
            if len(token) < min_token_length:
                continue

            best_candidate = None
            best_distance = None
            best_count = 0

            first_char = token[0]
            for length in range(len(token) - max_distance, len(token) + max_distance + 1):
                if length <= 0:
                    continue
                for candidate in candidate_index.get((first_char, length), []):
                    if candidate == token:
                        continue

                    candidate_count = token_counts[candidate]
                    if candidate_count < max(canonical_min_count, token_count * frequency_ratio):
                        continue

                    distance = self._levenshtein_distance_lte(token, candidate, max_distance)
                    if distance is None:
                        continue

                    if (
                        best_candidate is None
                        or candidate_count > best_count
                        or (candidate_count == best_count and distance < best_distance)
                    ):
                        best_candidate = candidate
                        best_distance = distance
                        best_count = candidate_count

            if best_candidate is not None:
                typo_map[token] = {
                    "canonical": best_candidate,
                    "distance": best_distance,
                    "count": token_count,
                    "canonical_count": best_count,
                }

        return typo_map

    def _collect_issue_rows(self, model_field_map, typo_map, spelling_standardization_map, chunk_size):
        issue_rows = []

        for model, fields in model_field_map:
            queryset = model.objects.only("pk", *fields).iterator(chunk_size=chunk_size)
            record_count = model.objects.count()
            progress = tqdm(
                queryset,
                total=record_count,
                desc=f"Issue scan {model.__name__}",
                unit="rec",
            )
            for instance in progress:
                instance_pk = instance.pk
                for field_name in fields:
                    value = getattr(instance, field_name, None)
                    if not isinstance(value, str) or not value.strip():
                        continue

                    issues = []
                    seen = set()
                    for raw_token in self._tokenize(value):
                        normalized_token = self._normalize_token(raw_token)
                        if normalized_token in typo_map:
                            typo_info = typo_map[normalized_token]
                            message = (
                                f"typo-like token '{raw_token}' -> '{typo_info['canonical']}' "
                                f"(distance={typo_info['distance']}, "
                                f"freq={typo_info['count']} vs {typo_info['canonical_count']})"
                            )
                            if message not in seen:
                                seen.add(message)
                                issues.append(message)

                        spelling_key = self._spelling_key(normalized_token)
                        spelling_info = spelling_standardization_map.get(spelling_key)
                        if spelling_info and raw_token.casefold() != spelling_info["preferred"].casefold():
                            variants_preview = ", ".join(spelling_info["variants"][:6])
                            message = (
                                f"alternate spelling '{raw_token}' -> prefer '{spelling_info['preferred']}' "
                                f"(family total={spelling_info['total']}; variants: {variants_preview})"
                            )
                            if message not in seen:
                                seen.add(message)
                                issues.append(message)

                        normalized_unicode = unicodedata.normalize("NFKC", raw_token)
                        if raw_token != normalized_unicode:
                            message = (
                                f"unicode variant '{raw_token}' -> '{normalized_unicode}' "
                                "(NFKC normalization)"
                            )
                            if message not in seen:
                                seen.add(message)
                                issues.append(message)

                    if issues:
                        issue_rows.append(
                            {
                                "model": model.__name__,
                                "field": field_name,
                                "pk": instance_pk,
                                "issues": issues,
                            }
                        )

        issue_rows.sort(key=lambda row: (row["model"], row["field"], row["pk"]))
        return issue_rows

    def _render_markdown_report(
        self,
        issue_rows,
        token_counts,
        raw_variant_counts,
        stats,
        top_limit,
        canonical_min_count,
        max_distance,
        min_token_length,
        frequency_ratio,
        variant_min_total,
    ):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        lines = [
            "# Token Quality Report",
            "",
            f"Generated: {now}",
            "",
            "## Scan Configuration",
            "",
            f"- Models scanned: {stats['models_scanned']}",
            f"- Records scanned: {stats['records_scanned']}",
            f"- Non-empty text/char fields scanned: {stats['non_empty_fields_scanned']}",
            f"- Unique normalized tokens: {len(token_counts)}",
            f"- Typo canonical minimum count: {canonical_min_count}",
            f"- Typo max Levenshtein distance: {max_distance}",
            f"- Typo minimum token length: {min_token_length}",
            f"- Typo minimum frequency ratio: {frequency_ratio}",
            f"- Alternate spelling family minimum total count: {variant_min_total}",
            "",
            "## Potential Issues By Record",
            "",
        ]

        if issue_rows:
            lines.extend(
                [
                    "| Model | Field | PK | Mistakes in Field |",
                    "|---|---|---:|---|",
                ]
            )
            for row in issue_rows:
                mistakes = "<br>".join(self._escape_md(item) for item in row["issues"])
                lines.append(
                    "| {model} | {field} | {pk} | {mistakes} |".format(
                        model=self._escape_md(row["model"]),
                        field=self._escape_md(row["field"]),
                        pk=row["pk"],
                        mistakes=mistakes,
                    )
                )
        else:
            lines.append("No potential typo-like or unicode-normalization issues detected.")

        lines.extend(["", f"## Top {top_limit} Repeated Tokens", ""])
        lines.extend(["| Rank | Token | Count |", "|---:|---|---:|"])

        for rank, (token, count) in enumerate(token_counts.most_common(top_limit), start=1):
            representative = raw_variant_counts[token].most_common(1)[0][0]
            lines.append(
                f"| {rank} | {self._escape_md(representative)} | {count} |"
            )

        lines.append("")
        return "\n".join(lines)

    def _tokenize(self, text):
        return self.TOKEN_RE.findall(text)

    def _normalize_token(self, token):
        token = unicodedata.normalize("NFKC", token).casefold().strip()
        return token

    def _spelling_key(self, token):
        decomposed = unicodedata.normalize("NFKD", token)
        without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
        return without_marks

    def _escape_md(self, text):
        return str(text).replace("|", "\\|").replace("\n", " ")

    def _levenshtein_distance_lte(self, source, target, max_distance):
        if abs(len(source) - len(target)) > max_distance:
            return None

        previous_row = list(range(len(target) + 1))

        for i, source_char in enumerate(source, start=1):
            current_row = [i]
            row_min = current_row[0]

            for j, target_char in enumerate(target, start=1):
                insert_cost = current_row[j - 1] + 1
                delete_cost = previous_row[j] + 1
                replace_cost = previous_row[j - 1] + (source_char != target_char)
                distance = min(insert_cost, delete_cost, replace_cost)
                current_row.append(distance)

                if distance < row_min:
                    row_min = distance

            if row_min > max_distance:
                return None

            previous_row = current_row

        final_distance = previous_row[-1]
        if final_distance > max_distance:
            return None
        return final_distance
