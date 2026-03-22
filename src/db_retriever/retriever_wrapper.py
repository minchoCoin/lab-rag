import argparse
import json
import sys
from typing import Any

from retriever import Retriever, RetrievalFilters

import warnings

warnings.filterwarnings("ignore")


def build_filters_from_args(args: argparse.Namespace) -> RetrievalFilters:
    return RetrievalFilters(
        source_type=args.source_type,
        speaker=args.speaker,
        seminar_date=args.seminar_date,
        start_date=args.start_date,
        end_date=args.end_date,
        year=args.year,
        month=args.month,
        week=args.week,
        filepath_keywords=args.filepath_keyword,
    )


def print_json(data: Any):
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def handle_filter(args: argparse.Namespace, retriever: Retriever):
    filters = build_filters_from_args(args)
    results = retriever.filter_only(filters=filters, limit=args.limit)
    print_json(results)


def handle_keyword(args: argparse.Namespace, retriever: Retriever):
    filters = build_filters_from_args(args)
    results = retriever.keyword_search(
        query=args.query,
        filters=filters,
        limit=args.limit,
    )
    print_json(results)


def handle_vector(args: argparse.Namespace, retriever: Retriever):
    filters = build_filters_from_args(args)
    results = retriever.vector_search(
        query=args.query,
        filters=filters,
        limit=args.limit,
    )
    print_json(results)


def handle_title_vector(args: argparse.Namespace, retriever: Retriever):
    filters = build_filters_from_args(args)
    results = retriever.title_vector_search(
        query=args.query,
        filters=filters,
        limit=args.limit,
    )
    print_json(results)


def handle_hybrid(args: argparse.Namespace, retriever: Retriever):
    filters = build_filters_from_args(args)
    results = retriever.hybrid_search(
        query=args.query,
        filters=filters,
        keyword_limit=args.keyword_limit,
        vector_limit=args.vector_limit,
        final_limit=args.limit,
    )
    print_json(results)


def handle_document(args: argparse.Namespace, retriever: Retriever):
    text = retriever.get_document_text(document_id=args.document_id)
    print_json({
        "document_id": args.document_id,
        "text": text,
    })


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Retriever CLI wrapper for metadata / keyword / vector / title-vector / hybrid search"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_filter_args(p: argparse.ArgumentParser):
        p.add_argument("--source-type", choices=["lab_seminar", "weekly_report"])
        p.add_argument("--speaker")
        p.add_argument("--seminar-date", help="YYYY-MM-DD")
        p.add_argument("--start-date", help="YYYY-MM-DD")
        p.add_argument("--end-date", help="YYYY-MM-DD")
        p.add_argument("--year", type=int)
        p.add_argument("--month", type=int)
        p.add_argument("--week", type=int)
        p.add_argument("--limit", type=int, default=10)
        p.add_argument("--filepath-keyword",action="append",dest="filepath_keyword",help="filepath에 포함되어야 하는 키워드. 여러 번 지정 가능",)

    # filter
    parser_filter = subparsers.add_parser(
        "filter",
        help="Metadata-only retrieval"
    )
    add_common_filter_args(parser_filter)
    parser_filter.set_defaults(func=handle_filter)

    # keyword
    parser_keyword = subparsers.add_parser(
        "keyword",
        help="Keyword search with optional filters"
    )
    parser_keyword.add_argument("--query", required=True)
    add_common_filter_args(parser_keyword)
    parser_keyword.set_defaults(func=handle_keyword)

    # vector
    parser_vector = subparsers.add_parser(
        "vector",
        help="Chunk vector search with optional filters"
    )
    parser_vector.add_argument("--query", required=True)
    add_common_filter_args(parser_vector)
    parser_vector.set_defaults(func=handle_vector)

    # title-vector
    parser_title_vector = subparsers.add_parser(
        "title-vector",
        help="Title vector search with optional filters"
    )
    parser_title_vector.add_argument("--query", required=True)
    add_common_filter_args(parser_title_vector)
    parser_title_vector.set_defaults(func=handle_title_vector)

    # hybrid
    parser_hybrid = subparsers.add_parser(
        "hybrid",
        help="Hybrid search with optional filters"
    )
    parser_hybrid.add_argument("--query", required=True)
    add_common_filter_args(parser_hybrid)
    parser_hybrid.add_argument("--keyword-limit", type=int, default=10)
    parser_hybrid.add_argument("--vector-limit", type=int, default=10)
    parser_hybrid.set_defaults(func=handle_hybrid)

    # document
    parser_document = subparsers.add_parser(
        "document",
        help="Get full document text by document_id"
    )
    parser_document.add_argument("--document-id", type=int, required=True)
    parser_document.set_defaults(func=handle_document)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        retriever = Retriever()
        args.func(args, retriever)
    except Exception as e:
        error_payload = {
            "error": type(e).__name__,
            "message": str(e),
        }
        print(json.dumps(error_payload, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()