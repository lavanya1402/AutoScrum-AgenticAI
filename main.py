import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory

# 🧠 Custom modules
from agents.sprint_planner import SprintPlannerAgent
from agents.risk_detector import RiskDetectorAgent
from agents.report_generator import ReportGeneratorAgent
from prompts.prompt_loader import load_prompt
from utils.load_data import load_backlog, format_backlog_as_text

# 🔐 Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ Please set your OPENAI_API_KEY in the .env file.")
    st.stop()

# 🧠 Load LLM and Memory
llm = ChatOpenAI(api_key=api_key, model_name="gpt-4", temperature=0)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# 🧑‍💻 Initialize Agents
planner_agent = SprintPlannerAgent(llm=llm, memory=memory)
risk_agent = RiskDetectorAgent(llm=llm, memory=memory)
report_agent = ReportGeneratorAgent(llm=llm, memory=memory)

# ✅ Initialize session state for sprint plan
if "sprint_plan" not in st.session_state:
    st.session_state.sprint_plan = ""

# 🎨 Streamlit UI
st.set_page_config(page_title="AutoScrum Agentic AI", layout="wide")
st.title("🤖 AutoScrum: True Agentic AI for Sprint Planning")
uploaded_file = st.file_uploader("📂 Upload your backlog CSV", type="csv")

# 📅 Generate next 10 working days (Mon–Fri)
def get_working_days(num_days=10):
    today = datetime.today()
    working_days = []
    current = today
    while len(working_days) < num_days:
        if current.weekday() < 5:
            working_days.append(current.strftime("%A, %d %B %Y"))
        current += timedelta(days=1)
    return working_days

working_days = get_working_days()
placeholders = {
    "{{START_DATE}}": working_days[0],
    "{{END_DATE}}": working_days[-1],
    "{{WORKING_DAYS_LIST}}": "\n".join(working_days)
}
for i in range(1, len(working_days)):
    placeholders[f"{{{{START_DATE + {i}}}}}"] = working_days[i]

# 📊 If file is uploaded
if uploaded_file:
    df = load_backlog(uploaded_file)
    st.dataframe(df)
    backlog_text = format_backlog_as_text(df)

    # 🔍 Ask general question about backlog
    user_query = st.text_input("💬 Ask a question about your backlog (optional):")
    if user_query:
        with st.spinner("🤔 Thinking..."):
            query_prompt = f"""
You are a helpful AI Scrum Assistant. Based on the following backlog, answer the user's question.

Backlog:
{backlog_text}

User's Question:
{user_query}

Answer:"""
            response = llm.invoke(query_prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            st.markdown("### 🔍 AI Response")
            st.write(content)

    # 🚦 Action Selector
    action = st.selectbox("📌 Choose an AI Action:", ["None", "Sprint Planning", "Risk Report", "Summary Report"])
    report_output = ""

    # 🧭 Sprint Planning
    if action == "Sprint Planning":
        with st.spinner("📋 Generating Sprint Plan..."):
            prompt = load_prompt("sprint_prompt.txt")
            for k, v in placeholders.items():
                prompt = prompt.replace(k, v)
            prompt = prompt.replace("{{TASKS}}", backlog_text)
            sprint_plan = planner_agent.run(prompt)
            st.session_state.sprint_plan = sprint_plan
            report_output = sprint_plan
            st.markdown("### ✅ Sprint Plan")
            st.write(sprint_plan)
            st.success("✅ Sprint Plan is saved and ready for Risk Detection.")

    # ⚠️ Risk Report (based on Sprint Plan)
    elif action == "Risk Report":
        if not st.session_state.sprint_plan:
            st.warning("⚠️ Please generate Sprint Plan first before running Risk Report.")
        else:
            with st.spinner("🚨 Detecting Risks..."):
                prompt = load_prompt("risk_prompt.txt")
                prompt = prompt.replace("{{TASKS}}", st.session_state.sprint_plan)
                risk_report = risk_agent.run(prompt)
                report_output = risk_report
                st.markdown("### ⚠️ Risk Report")
                st.write(risk_report)

    # 📝 Summary Report (based on Sprint + Risk)
    elif action == "Summary Report":
        if not st.session_state.sprint_plan:
            st.warning("⚠️ Please generate Sprint Plan first.")
        else:
            with st.spinner("📝 Generating Final Summary..."):
                risk_prompt = load_prompt("risk_prompt.txt").replace("{{TASKS}}", st.session_state.sprint_plan)
                risk_report = risk_agent.run(risk_prompt)
                combined_context = f"Sprint Plan:\n{st.session_state.sprint_plan}\n\nRisks:\n{risk_report}"
                final_prompt = load_prompt("report_prompt.txt").replace("{{TASKS}}", combined_context)
                final_report = report_agent.run(final_prompt)
                report_output = final_report
                st.markdown("### 🧾 Final Summary Report")
                st.write(final_report)

    # 🧠 Follow-up Question
    if action != "None" and report_output:
        follow_up = st.text_input("🧠 Ask a follow-up question about the result (optional):")
        if follow_up:
            with st.spinner("🔄 Thinking..."):
                follow_up_prompt = f"""
You are a smart AI assistant. Based on the response below, answer the follow-up question.

Response:
{report_output}

Follow-up Question:
{follow_up}

Answer:"""
                follow_response = llm.invoke(follow_up_prompt)
                follow_text = follow_response.content if hasattr(follow_response, "content") else str(follow_response)
                st.markdown("### 🔍 Follow-Up Response")
                st.write(follow_text)

else:
    st.info("👆 Please upload a backlog CSV to get started.")
