import streamlit as st
import pandas as pd
import numpy as np
import openpyxl as xl
import drawio_client as drawio


def main():
    st.title("Maker-Checker Process for Sending Funds")

    process_steps = [
        {"id": "start", "label": "Start", "shape": "ellipse"},
        {"id": "maker_initiate", "label": "Maker Initiates Fund Transfer Request", "shape": "rectangle"},
        {"id": "maker_enter_details", "label": "Enters Beneficiary Details, Amount, Purpose, etc.", "shape": "rectangle"},
        {"id": "maker_submit", "label": "Submits Request for Approval", "shape": "rectangle"},
        {"id": "checker_notify", "label": "Checker Receives Notification", "shape": "rectangle"},
        {"id": "checker_review", "label": "Checker Reviews Transaction Details", "shape": "rectangle"},
        {"id": "check_correct", "label": "Transaction Details Correct?", "shape": "rhombus"},
        {"id": "checker_approve", "label": "Checker Approves Transaction", "shape": "rectangle"},
        {"id": "transaction_processed", "label": "Transaction Processed (Funds Sent)", "shape": "rectangle", "style": "fillColor=#d5e8d4;strokeColor=#82b366;"},
        {"id": "end_success", "label": "End", "shape": "ellipse"},
        {"id": "checker_reject", "label": "Checker Rejects Transaction", "shape": "rectangle", "style": "fillColor=#f8cecc;strokeColor=#b85450;"},
        {"id": "notify_maker_reject", "label": "Notification Sent to Maker with Reason for Rejection", "shape": "rectangle"},
        {"id": "maker_review_reject", "label": "Maker Reviews Rejection and Corrects/Cancels Request", "shape": "rectangle"},
        {"id": "repeat_or_end", "label": "Repeat or End", "shape": "ellipse"},
    ]

    connections = [
        {"source": "start", "target": "maker_initiate"},
        {"source": "maker_initiate", "target": "maker_enter_details"},
        {"source": "maker_enter_details", "target": "maker_submit"},
        {"source": "maker_submit", "target": "checker_notify"},
        {"source": "checker_notify", "target": "checker_review"},
        {"source": "checker_review", "target": "check_correct"},
        {"source": "check_correct", "target": "checker_approve", "label": "Yes"},
        {"source": "checker_approve", "target": "transaction_processed"},
        {"source": "transaction_processed", "target": "end_success"},
        {"source": "check_correct", "target": "checker_reject", "label": "No"},
        {"source": "checker_reject", "target": "notify_maker_reject"},
        {"source": "notify_maker_reject", "target": "maker_review_reject"},
        {"source": "maker_review_reject", "target": "repeat_or_end"},
        {"source": "repeat_or_end", "target": "maker_initiate", "label": "Repeat"}, # Optional: Loop back
        {"source": "repeat_or_end", "target": "end_success", "label": "End"},    # Optional: End from repeat
    ]

    # Define swimlanes
    swimlanes = [
        {"id": "maker_lane", "label": "Maker"},
        {"id": "checker_lane", "label": "Checker"},
        {"id": "system_lane", "label": "System"},
    ]

    # Assign steps to swimlanes (adjust as needed)
    step_lanes = {
        "start": "maker_lane",
        "maker_initiate": "maker_lane",
        "maker_enter_details": "maker_lane",
        "maker_submit": "maker_lane",
        "checker_notify": "checker_lane",
        "checker_review": "checker_lane",
        "check_correct": "checker_lane",
        "checker_approve": "checker_lane",
        "transaction_processed": "system_lane",
        "end_success": "system_lane",
        "checker_reject": "checker_lane",
        "notify_maker_reject": "system_lane",
        "maker_review_reject": "maker_lane",
        "repeat_or_end": "maker_lane",
    }

    # --- Option 1: Using a Placeholder for drawio (if direct rendering isn't available) ---
    st.subheader("Diagram Placeholder")
    st.info("This section would ideally display the draw.io diagram. You might need a specific Streamlit component or integration to render it directly from a definition.")
    st.write("The process flow is described below.")

    # --- Option 2: Generating a drawio XML string (for download or external use) ---
    xml_string = drawio.generate_xml(process_steps, connections, swimlanes=swimlanes, step_lanes=step_lanes)
    st.download_button(
        label="Download draw.io XML",
        data=xml_string,
        file_name="maker_checker_process.drawio.xml",
        mime="application/xml"
    )

    st.subheader("Process Flow Explanation:")
    st.markdown("""
    1.  **Start:** The process begins when there's a need to send funds.

    2.  **Maker Initiates Fund Transfer Request:** An authorized user (the Maker) starts the process within the system.

    3.  **Enters Beneficiary Details, Amount, Purpose, etc.:** The Maker inputs all necessary transaction details.

    4.  **Submits Request for Approval:** The Maker submits the request, making it ready for the Checker's review.

    5.  **Checker Receives Notification:** An authorized and different user (the Checker) is notified about the pending request.

    6.  **Checker Reviews Transaction Details:** The Checker carefully examines all the entered information for accuracy and compliance.

    7.  **Transaction Details Correct?:** The Checker makes a decision:
        * **Yes:** If everything is correct, the process proceeds to approval.
        * **No:** If there are errors or issues, the transaction is rejected.

    8.  **Checker Approves Transaction:** The Checker approves the request in the system.

    9.  **Transaction Processed (Funds Sent):** The system executes the fund transfer.

    10. **End:** The fund transfer is successfully completed.

    11. **Checker Rejects Transaction:** The Checker rejects the request, halting the process.

    12. **Notification Sent to Maker with Reason for Rejection:** The Maker receives a notification explaining why their request was rejected.

    13. **Maker Reviews Rejection and Corrects/Cancels Request:** The Maker reviews the feedback, makes necessary corrections, or cancels the request.

    14. **Repeat or End:** The Maker can either resubmit the corrected request (going back to step 3 or 4) or decide to end the process.
    """)

if __name__ == "__main__":
    main()
