import google.generativeai as genai
import streamlit as st
import re  

class AiCodeReviewer:
    def __init__(self):
        self.key = "YOUR_API_KEY" 

    def chatbot(self, system_instruction: str = None):
        try:
            genai.configure(api_key=self.key)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_instruction
            )
            return model.start_chat()
        except Exception as e:
            st.error(f"Error initializing AI model: {e}")
            return None

    def check_syntax_and_fix(self, code: str):
        """Checks for syntax errors and attempts to fix indentation automatically."""
        try:
            compile(code, "<string>", "exec")
            return None, code 
        except SyntaxError as e:
            error_msg = f"Syntax Error: {e}"
            return error_msg, None

    def extract_feedback(self, response_text):
        """Extracts Bug Report and Fixed Code using regex."""
        bug_report_match = re.search(r"\*\*Bug Report:\*\*\s*(.*?)(?=\*\*Fixed Code:|\Z)", response_text, re.DOTALL)
        fixed_code_match = re.search(r"\*\*Fixed Code:\*\*\s*(?:```python)?\n(.+?)```", response_text, re.DOTALL)

        bug_report = bug_report_match.group(1).strip() if bug_report_match else "No specific issues detected."
        fixed_code = fixed_code_match.group(1).strip() if fixed_code_match else "No fixed code generated."

        return bug_report.split("\n"), fixed_code

    def streamlit_app(self):
        st.markdown("""
            <style>
                .title { text-align: left; font-size: 20px; color: #333; font-weight: bold; }
                .subheader { text-align: left; color: #555; font-size: 14px; }
                .code-box { background-color: #f5f5f5; padding: 8px; border-radius: 3px; font-family: monospace; font-size: 12px; }
                .stTextArea textarea { font-size: 12px; }
                .stButton button { font-size: 14px; }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<div class='title'>AI Code Reviewer</div>", unsafe_allow_html=True)
        st.markdown("<div class='subheader'>Enter your Python code below:</div>", unsafe_allow_html=True)

        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        instruction = """
        You are an expert AI code reviewer. Analyze the provided Python code for clarity, efficiency, maintainability,
        and adherence to best practices. Identify syntax errors, logic flaws, and suggest optimizations.

        Always provide a response in the following strict format:

        **Bug Report:**
        (List all issues clearly)

        **Fixed Code:**
        ```python
        (Corrected code here)
        ```
        """

        chat = self.chatbot(instruction)
        if not chat:
            return

        chat.history = st.session_state["chat_history"]

        user_prompt = st.text_area("", height=150)

        if st.button("Generate Code Review"):
            if user_prompt.strip():
                st.markdown("<div class='subheader'>Code Review</div>", unsafe_allow_html=True)

                syntax_error, auto_fixed_code = self.check_syntax_and_fix(user_prompt)

                if syntax_error:
                    st.markdown("<div class='subheader'>Bug Report</div>", unsafe_allow_html=True)
                    for line in syntax_error.split("\n"):
                        st.text(line)

                    if auto_fixed_code:
                        st.markdown("<div class='subheader'>Fixed Code</div>", unsafe_allow_html=True)
                        st.code(auto_fixed_code, language="python")
                    return  

                with st.spinner("Analyzing your code..."):
                    response = chat.send_message(user_prompt)
                    if not response or not hasattr(response, "text"):
                        st.error("Failed to generate a response. Please try again.")
                        return

                bug_report, fixed_code = self.extract_feedback(response.text)

                st.markdown("<div class='subheader'>Bug Report</div>", unsafe_allow_html=True)
                for line in bug_report:
                    st.text(line)

                st.markdown("<div class='subheader'>Fixed Code</div>", unsafe_allow_html=True)
                st.code(fixed_code, language="python")

                st.session_state["chat_history"] = chat.history
            else:
                st.warning("Please enter your Python code before clicking review.")

if __name__ == "__main__":
    ai = AiCodeReviewer()
    ai.streamlit_app()
