// BEC Email Analyzer - Gmail Content Script

function getEmailData() {
    let sender = "Unknown sender";
    let subject = "No subject";
    let body = "";

    // Get subject
    const subjectElement = document.querySelector("h2.hP");

    if (subjectElement) {
        subject = subjectElement.innerText.trim();
    }

    // Get sender
    const senderElement = document.querySelector(
        ".gD"
    );

    if (senderElement) {
        sender =
            senderElement.getAttribute("email") ||
            senderElement.innerText.trim();
    }

    // Get email body
    const bodyElement = document.querySelector(
        ".a3s.aiL"
    );

    if (bodyElement) {
        body = bodyElement.innerText.trim();
    }

    return {
        sender: sender,
        subject: subject,
        body: body
    };
}


// Listen for requests from popup.js
chrome.runtime.onMessage.addListener(
    (message, sender, sendResponse) => {

        if (message.action === "getEmail") {

            const emailData = getEmailData();

            console.log("BEC Analyzer - Email Data:", emailData);

            sendResponse(emailData);
        }

        return true;
    }
);