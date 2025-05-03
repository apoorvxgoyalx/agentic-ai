# Agentic AI for Cloud Operations

A natural-language assistant to manage OpenStack-based cloud infrastructure using LLMs and automation workflows.

---

## 📽️ Demo Video

[Watch Demo Video]( [https://drive.google.com/file/d/1dwCo_um8cmvuZLQHHj0tbBAOsKWC0RTl/view?usp=sharing] )

---

## 📄 SRS Document

[SRS PDF Link](https://drive.google.com/file/d/1J8vv0vKb9hFhMD0BwCXqFhLCnN2w81VV/view?usp=sharing)

---

## 📊 SRS Presentation (PPT)

[SRS Presentation Link](https://docs.google.com/presentation/d/1ejZN1X1CZu0eRY1pIlBw_Z22XxxJrbuk/edit?usp=sharing&ouid=115259450870590112305&rtpof=true&sd=true)

---

## 🛠️ Installation Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/apoorvxgoyalx/agentic-ai.git
cd agentic-ai
```

### Step 2: Set Up a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Required Dependencies

```bash
pip install -r requirements.txt
```

> If `requirements.txt` is not available, use:

```bash
pip install streamlit==1.32.0 \
            groq==0.4.0 \
            python-dotenv==1.0.0 \
            openstacksdk==2.0.0
```

### Step 4: Environment Variables

Create a `.env` file in the root folder and add the necessary API keys and OpenStack credentials:

```env
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key
OS_AUTH_URL=your_openstack_auth_url
OS_USERNAME=your_username
OS_PASSWORD=your_password
OS_PROJECT_NAME=your_project
OS_USER_DOMAIN_NAME=Default
OS_PROJECT_DOMAIN_NAME=Default
```

### Step 5: Run the Application

```bash
streamlit run app.py
```

> Replace `app.py` with the actual entrypoint script if named differently.

---

## ✅ Features

* Natural Language Instructions → OpenStack API Calls
* VM provisioning, resizing, deletion
* Network and volume management
* Interactive chatbot via Streamlit UI
* Backed by OpenStack SDK and Groq for fast inference

---

## 📦 Tech Stack

* **Frontend**: Streamlit
* **Backend**: Python
* **Cloud API**: OpenStack SDK (Nova, Neutron, Cinder)
* **LLM**: Groq + OpenAI (optional)
* **Environment Management**: dotenv

---

## 🙋 Contributing

1. Fork this repo
2. Create your feature branch (`git checkout -b feature/xyz`)
3. Commit your changes (`git commit -m 'Add xyz'`)
4. Push to the branch (`git push origin feature/xyz`)
5. Create a Pull Request

---

## 📬 Contact

For queries, contact [Apoorv Goyal](mailto:your-email@example.com) or raise an issue.

---

> ✨ Let's make OpenStack operations conversational!
