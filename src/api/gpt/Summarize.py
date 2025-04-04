from GptSummarize import GptSummarize

__summarize = GptSummarize()

def summarize(reviews: list[str]) -> str:
    __summarize.clear_messages()
    __summarize.append_review(reviews)
    return __summarize.summarize()
    