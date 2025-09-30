from flask import Flask, request, render_template, send_file
import joblib
import pandas as pd
from fpdf import FPDF
import os
import numpy as np 

# --- CRITICAL FIX 1: Explicitly set template path ---
# We define the Flask app and tell it where the templates are located.

TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=TEMPLATE_DIR)


# === Job Role Information (Mapped to ENCODED numbers) ===
# NOTE: This information is defined globally as it is static and required by the prediction logic.
JOB_ROLE_INFO_MAP = {}
original_job_info = { 
    "Database Developer": { "Description": "Focuses on creating and managing databases...", "Skills": "SQL, database design...", "PotentialCompanies": "TCS, Infosys..." },
    "Portal Administrator": { "Description": "Manages user accounts, permissions...", "Skills": "CMS (SharePoint, Drupal)...", "PotentialCompanies": "HCLTech, Wipro..." },
    "Systems Security Administrator": { "Description": "Ensures the security of an organization's IT infrastructure...", "Skills": "Firewalls, intrusion detection...", "PotentialCompanies": "McAfee, Palo Alto Networks..." },
    "Business Systems Analyst": { "Description": "Acts as a liaison between business stakeholders and IT teams...", "Skills": "Business analysis, documentation...", "PotentialCompanies": "TCS, Infosys, Wipro..." },
    "Software Systems Engineer": { "Description": "Designs, develops, and maintains software systems...", "Skills": "Java, Python, C++, software design...", "PotentialCompanies": "Google, Microsoft, Amazon..." },
    "Business Intelligence Analyst": { "Description": "Uses data analysis tools to generate insights...", "Skills": "Tableau, Power BI, SAP BusinessObjects...", "PotentialCompanies": "Flipkart, Amazon India..." },
    "CRM Technical Developer": { "Description": "Develops and customizes CRM software solutions...", "Skills": "CRM platforms (Salesforce, Microsoft Dynamics)...", "PotentialCompanies": "Salesforce, Microsoft, Oracle..." },
    "Mobile Applications Developer": { "Description": "Develops applications for smartphones and tablets...", "Skills": "Swift/Objective-C (iOS), Java/Kotlin (Android)...", "PotentialCompanies": "Byju's, Swiggy, Zomato..." },
    "UX Designer": { "Description": "Designs user experiences for websites and applications...", "Skills": "Wireframing, prototyping, user testing...", "PotentialCompanies": "Apple, Google, Amazon..." },
    "Quality Assurance Associate": { "Description": "Ensures the quality of software applications through testing...", "Skills": "Manual testing, automation testing (Selenium, JUnit)...", "PotentialCompanies": "Accenture, Capgemini, Cognizant..." },
    "Web Developer": { "Description": "Designs and develops websites and web applications...", "Skills": "HTML, CSS, JavaScript, React, Angular...", "PotentialCompanies": "Google, Facebook, LinkedIn..." },
    "Information Security Analyst": { "Description": "Monitors and protects an organization's IT infrastructure...", "Skills": "Network security, encryption, firewalls...", "PotentialCompanies": "McAfee, Symantec, Palo Alto Networks..." },
    "CRM Business Analyst": { "Description": "Analyzes and defines business requirements for CRM systems...", "Skills": "CRM tools (Salesforce, Microsoft Dynamics)...", "PotentialCompanies": "Salesforce, Microsoft, Oracle..." },
    "Technical Support": { "Description": "Provides technical assistance to clients...", "Skills": "Problem-solving, troubleshooting, networking...", "PotentialCompanies": "Dell, HP, IBM..." },
    "Project Manager": { "Description": "Manages IT projects, coordinating teams, timelines...", "Skills": "Project management, Agile, Scrum...", "PotentialCompanies": "TCS, Infosys, Cognizant..." },
    "Information Technology Manager": { "Description": "Oversees the IT department and its operations...", "Skills": "IT management, team leadership...", "PotentialCompanies": "Cisco, IBM, Wipro..." },
    "Programmer Analyst": { "Description": "Develops and maintains software applications based on business requirements...", "Skills": "Java, C++, Python, SQL...", "PotentialCompanies": "TCS, Wipro, Cognizant..." },
    "Design & UX": { "Description": "Focuses on designing the user experience of digital products...", "Skills": "Wireframing, prototyping, user testing...", "PotentialCompanies": "Apple, Google, Microsoft..." },
    "Solutions Architect": { "Description": "Designs and implements technology solutions to meet business needs...", "Skills": "System architecture, cloud computing...", "PotentialCompanies": "Amazon, Microsoft, Google..." },
    "Systems Analyst": { "Description": "Analyzes and designs IT systems and software...", "Skills": "System analysis, programming...", "PotentialCompanies": "IBM, Oracle, TCS..." },
    "Network Security Administrator": { "Description": "Monitors and manages network security infrastructure...", "Skills": "Firewall configuration, VPN, intrusion detection...", "PotentialCompanies": "Cisco, Palo Alto Networks..." },
    "Data Architect": { "Description": "Designs and manages data systems...", "Skills": "Data modeling, database design...", "PotentialCompanies": "Google, Amazon, Microsoft..." },
    "Software Developer": { "Description": "Develops, tests, and maintains software applications...", "Skills": "Java, Python, C++, software design...", "PotentialCompanies": "TCS, Infosys, Wipro..." },
    "E-Commerce Analyst": { "Description": "Analyzes e-commerce trends, user behavior...", "Skills": "Google Analytics, SEO, SEM...", "PotentialCompanies": "Amazon, Flipkart, Walmart..." },
    "Technical Services/Help Desk/Tech Support": { "Description": "Provides technical assistance and support to end-users...", "Skills": "Technical troubleshooting, customer service...", "PotentialCompanies": "Dell, HP, IBM..." },
    "Information Technology Auditor": { "Description": "Conducts audits of IT systems and processes...", "Skills": "Auditing, risk assessment, compliance...", "PotentialCompanies": "PwC, KPMG, Deloitte..." },
    "Database Manager": { "Description": "Manages database systems and their performance...", "Skills": "Database management, SQL, DBMS (Oracle, MySQL)...", "PotentialCompanies": "TCS, Infosys, Wipro..." },
    "Applications Developer": { "Description": "Designs, develops, and tests software applications...", "Skills": "Java, Python, application development...", "PotentialCompanies": "Google, Microsoft, Amazon..." },
    "Database Administrator": { "Description": "Manages and maintains databases...", "Skills": "SQL, Oracle, MySQL, database backup...", "PotentialCompanies": "TCS, Infosys, Wipro..." },
    "Network Engineer": { "Description": "Designs, implements, and maintains network infrastructure...", "Skills": "TCP/IP, VPN, network protocols...", "PotentialCompanies": "Cisco, Juniper Networks..." },
    "Software Engineer": { "Description": "Designs, develops, and tests software systems...", "Skills": "Java, Python, C++, software design patterns...", "PotentialCompanies": "Google, Microsoft, Amazon..." },
    "Technical Engineer": { "Description": "Provides technical expertise for hardware and software systems...", "Skills": "System installation, hardware troubleshooting...", "PotentialCompanies": "Hewlett Packard, Dell, IBM..." },
    "Network Security Engineer": { "Description": "Designs and implements secure networks...", "Skills": "Firewall management, network security protocols...", "PotentialCompanies": "Cisco, Palo Alto Networks..." },
    "Software Quality Assurance (QA) / Testing": { "Description": "Ensures software quality by testing and identifying defects...", "Skills": "Manual testing, automation (Selenium)...", "PotentialCompanies": "Cognizant, Accenture, Wipro..." }
}

# NOTE: The model and encoder are loaded INSIDE the predict function (lazy loading)
# to ensure they are available after the training script creates them.

@app.route('/')
def home():
    # Render the HTML template
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    
    # === CRITICAL FIX 2: Load Model Assets Inside the Function ===
    # We must load the assets now because the training script has already run
    # and created them on the server's disk.
    try:
        model = joblib.load('model.pkl')
        scaler = joblib.load('scaler.pkl') 
        feature_columns = joblib.load('columns.pkl') 
        le = joblib.load('le.pkl') 
    except Exception as e:
        # If model loading fails here, the assets were not created by the build command.
        print(f"FATAL ERROR: Model assets not created: {e}")
        return render_template('newui.html', prediction_text='Deployment Error: Model assets not found on server.')

    # Map the job roles to the loaded LabelEncoder classes
    JOB_ROLE_INFO_MAP_FINAL = {}
    if model and le: 
        for i, role_name in enumerate(le.classes_):
            JOB_ROLE_INFO_MAP_FINAL[i] = original_job_info.get(role_name, { 
                "Role": role_name, 
                "Description": "Details not available in the database.", 
                "Skills": "N/A", 
                "PotentialCompanies": "N/A"
            })
    
    # --- Start Prediction Logic ---
    try:
        form_values = request.form.to_dict()
        processed_input = {}
        
        # === 1. Pre-Processing: Type Conversion ===
        for key, value in form_values.items():
            if isinstance(value, str):
                if value.lower() == 'yes':
                    processed_input[key] = 1.0
                elif value.lower() == 'no':
                    processed_input[key] = 0.0
                else:
                    try:
                        processed_input[key] = float(value)
                    except ValueError:
                        processed_input[key] = value
            else:
                processed_input[key] = value

        input_df = pd.DataFrame([processed_input])

        # === 2. Domain Feature Engineering (Must match the training script exactly) ===
        input_df['Knowledge Engineering'] = (input_df['percentage in Algorithms'] + input_df['Percentage in Mathematics']) / 2
        input_df['System Engineering'] = (
            input_df['Acedamic percentage in Operating Systems'] +
            input_df['Percentage in Computer Architecture'] +
            input_df['Percentage in Electronics Subjects']) / 3
        input_df['Networks and Security'] = (
            input_df['Percentage in Computer Networks'] +
            input_df['Percentage in Communication skills']) / 2
        input_df['Software Development'] = (
            input_df['Percentage in Programming Concepts'] +
            input_df['Percentage in Software Engineering']) / 2
        input_df['Professional Development'] = (
            input_df['Percentage in Communication skills'] +
            input_df['Percentage in Mathematics']) / 2

        # Drop the original columns used for engineering
        input_df.drop([ 
            'percentage in Algorithms', 'Percentage in Mathematics',
            'Acedamic percentage in Operating Systems',
            'Percentage in Computer Architecture',
            'Percentage in Electronics Subjects',
            'Percentage in Computer Networks',
            'Percentage in Communication skills',
            'Percentage in Programming Concepts',
            'Percentage in Software Engineering'
        ], axis=1, inplace=True, errors='ignore')

        # === 3. Final Pre-processing (Scaling and Reindexing) ===
        input_df = pd.get_dummies(input_df)
        
        # Align columns with the feature_columns list (from columns.pkl)
        input_df = input_df.reindex(columns=feature_columns, fill_value=0)
        
        # Apply Scaling
        input_scaled = scaler.transform(input_df)
        
        # === 4. Predict and Decode ===
        prediction_numeric = model.predict(input_scaled)[0]
        decoded_prediction = le.inverse_transform([prediction_numeric])[0]

        # === 5. PDF Generation and Retrieval ===
        role_info = JOB_ROLE_INFO_MAP_FINAL.get(prediction_numeric, {})
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(200, 10, txt=f"Predicted Role: {decoded_prediction}", ln=True, align='C')
        pdf.ln(10) 
        
        # Content
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(200, 10, txt="Role Description:", ln=True, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 5, role_info.get('Description', 'No detailed description available.'))
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(200, 10, txt="Key Skills:", ln=True, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 5, role_info.get('Skills', 'N/A'))
        pdf.ln(5)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(200, 10, txt="Potential Companies:", ln=True, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 5, role_info.get('PotentialCompanies', 'N/A'))

        pdf_output_path = 'career_prediction.pdf'
        pdf.output(pdf_output_path)

        # Return the generated PDF file for download
        return send_file(pdf_output_path, as_attachment=True, download_name='career_prediction.pdf')

    except Exception as e:
        print(f"CRITICAL ERROR in prediction logic: {e}") 
        return render_template('newui.html', prediction_text=f' Prediction Error: {str(e)}. Please check inputs.')
    
if __name__ == '__main__':
    # This block is only for local testing. In production, gunicorn handles the run command.
    pass