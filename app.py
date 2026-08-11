import streamlit as st
import email_engine
import ai_engine
import calendar_engine

st.set_page_config(page_title="AI Sec-Assistant", page_icon="🛡️", layout="wide")
st.title("🛡️ Executive AI & Security Hub")

# 1. Initialize Memory State FIRST
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "schedule_context" not in st.session_state:
    st.session_state.schedule_context = ""

# 2. Render the Sidebar
with st.sidebar:
    st.header("📅 Upcoming Schedule")
    if st.button("Sync Calendar"):
        with st.spinner("Syncing..."):
            cal_service = calendar_engine.authenticate_calendar()
            events = calendar_engine.fetch_upcoming_events(cal_service)
            
            if not events:
                st.info("No upcoming events found.")
                st.session_state.schedule_context = "The user has no upcoming meetings."
            else:
                schedule_string = ""
                for event in events:
                    if "error" in event:
                        st.error(event["error"])
                    else:
                        display_time = event['start'].split("T")[0]
                        if "T" in event['start']:
                            display_time += f" at {event['start'].split('T')[1][:5]}"
                        
                        st.markdown(f"**{event['summary']}**")
                        st.caption(f"Time: {display_time}")
                        st.divider()
                        
                        schedule_string += f"- {event['summary']} on {display_time}\n"
                
                st.session_state.schedule_context = schedule_string

# 3. Create the Tabs (This was the missing line!)
tab1, tab2 = st.tabs(["📧 Inbox Auditor", "💬 Executive Chatbot"])

# --- TAB 1: EMAIL AUDITOR ---
with tab1:
    st.markdown("Automated Inbox Auditing, Threat Detection, and Summarization.")
    
    if st.button("Run Security Audit & Fetch Inbox"):
        with st.spinner("Processing live inbox..."):
            service = email_engine.authenticate_gmail()
            emails = email_engine.fetch_latest_emails(service)
            
            st.success(f"Successfully processed {len(emails)} emails!")
            
            for email in emails:
                with st.expander(f"{email.get('category', 'Unknown')} | {email.get('subject', 'No Subject')} (From: {email.get('sender', 'Unknown')})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown("**AI Summary:**")
                        st.info(email.get('summary', 'No summary available.'))
                        st.write(f"**Action Required:** {email.get('action_required', 'Unknown')}")
                        
                    with col2:
                        risk = email.get('risk_score', 0)
                        if risk == 0:
                            st.metric(label="Threat Score", value=f"{risk}%", delta="Safe", delta_color="normal")
                        else:
                            st.metric(label="Threat Score", value=f"{risk}%", delta="Critical", delta_color="inverse")
                            st.error(f"Link: {email.get('url_scanned', 'Unknown')}")

# --- TAB 2: CHATBOT ---
with tab2:
    st.markdown("Ask your assistant to draft emails, explain concepts, or check your schedule.")
    
    # Render previous messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Capture user input
    if prompt := st.chat_input("Type your message here..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        recent_history = "\n".join(
            [f"{m['role']}: {m['content']}" for m in st.session_state.chat_history[-4:]]
        )

        # Get AI response using the injected schedule context
        with st.spinner("Analyzing..."):
            ai_response = ai_engine.chat_with_assistant(
                prompt, 
                recent_history, 
                st.session_state.schedule_context
            )
        
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})