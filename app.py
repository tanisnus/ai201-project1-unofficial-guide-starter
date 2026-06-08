"""
app.py
Gradio query interface for the UC Transfer Unofficial Guide.
Run: python app.py
Requires: embed.py completed, GROQ_API_KEY in .env
"""

import gradio as gr

from generate import answer_query


def handle_query(question: str) -> str:
    result = answer_query(question)
    status = "Refused — insufficient context" if result.refused else "Answer generated from retrieved sources"
    return f"**Status:** {status}\n\n{result.answer}"


DESCRIPTION = """
Ask questions about **transferring from a California community college to a UC**.

Answers are generated **only** from retrieved document chunks. Sources are attached
programmatically at the end of every response.

**Example questions:**
- What is the minimum GPA to be eligible to transfer to a UC?
- How do I find which CC courses satisfy my major prep for a UC campus?
- Is a UC TAG a 100% guarantee once approved?
"""

with gr.Blocks(title="UC Transfer Unofficial Guide") as demo:
    gr.Markdown("# The Unofficial Guide — UC Transfer Q&A")
    gr.Markdown(DESCRIPTION)

    with gr.Row():
        question_input = gr.Textbox(
            label="Your question",
            placeholder="e.g. How many units do I need for junior standing at a UC?",
            lines=2,
            scale=4,
        )
        submit_btn = gr.Button("Ask", variant="primary", scale=1)

    answer_output = gr.Markdown(label="Answer")

    gr.Examples(
        examples=[
            ["What is the minimum GPA a California resident needs to be eligible to transfer to a UC?"],
            ["Is a UC TAG a 100% guarantee of admission once approved?"],
            ["How do I find which community college courses satisfy my major prep for a specific UC campus?"],
            ["How many units do I need to reach junior standing for UC transfer?"],
            ["What is the best pizza near UCLA?"],
        ],
        inputs=question_input,
    )

    submit_btn.click(
        fn=handle_query,
        inputs=question_input,
        outputs=answer_output,
    )
    question_input.submit(
        fn=handle_query,
        inputs=question_input,
        outputs=answer_output,
    )


if __name__ == "__main__":
    demo.launch()
