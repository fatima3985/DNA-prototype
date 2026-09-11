document.addEventListener("DOMContentLoaded", () => {

    const analyzeBtn = document.getElementById("analyzeBtn");

    analyzeBtn.addEventListener("click", async () => {

        analyzeBtn.textContent = "⏳ Reading email...";
        analyzeBtn.disabled = true;

        try {

            // Get the current browser tab
            const tabs = await chrome.tabs.query({
                active: true,
                currentWindow: true
            });

            const currentTab = tabs[0];

            // Get email data from Gmail
            const email = await chrome.tabs.sendMessage(
                currentTab.id,
                {
                    action: "getEmail"
                }
            );

            console.log("Email received:", email);

            // Display sender and subject
            document.getElementById("sender").textContent =
                email.sender;

            document.getElementById("subject").textContent =
                email.subject;


            // Send email to Python server
            analyzeBtn.textContent = "⏳ Analyzing...";

            const response = await fetch(
                "http://127.0.0.1:5000/analyze",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        sender: email.sender,
                        subject: email.subject,
                        body: email.body
                    })
                }
            );


            // Check server response
            if (!response.ok) {
                throw new Error(
                    "Python server returned an error."
                );
            }


            const result = await response.json();

            console.log(
                "Python analysis result:",
                result
            );


            // -----------------------------
            // Risk Assessment
            // -----------------------------

            document.getElementById("riskLevel").textContent =
                result.risk_label;

            document.getElementById("riskScore").textContent =
                result.risk_score + " / 100";


            // -----------------------------
            // Writing Score
            // -----------------------------

            document.getElementById("writingScore").textContent =
                result.writing_deviation;

            document.getElementById("writingBar").style.width =
                result.writing_deviation + "%";


            // -----------------------------
            // Behavior Score
            // -----------------------------

            document.getElementById("behaviorScore").textContent =
                result.behavior_score;

            document.getElementById("behaviorBar").style.width =
                result.behavior_score + "%";


            // -----------------------------
            // Reasons
            // -----------------------------

            const reasonsList =
                document.getElementById("reasons");

            reasonsList.innerHTML = "";


            if (
                result.reasons &&
                result.reasons.length > 0
            ) {

                result.reasons.forEach(reason => {

                    const li =
                        document.createElement("li");

                    li.textContent = reason;

                    reasonsList.appendChild(li);

                });

            } else {

                const li =
                    document.createElement("li");

                li.textContent =
                    "No significant red flags detected";

                reasonsList.appendChild(li);
            }


            // -----------------------------
            // Finished
            // -----------------------------

            analyzeBtn.textContent =
                "✓ Analysis Complete";

        }

        catch (error) {

            console.error(
                "BEC Analyzer Error:",
                error
            );

            analyzeBtn.textContent =
                "⚠️ Analysis Failed";

            alert(
                "Could not connect to the Python analyzer.\n\n" +
                "Make sure server.py is running."
            );
        }

        finally {

            analyzeBtn.disabled = false;

        }

    });

});