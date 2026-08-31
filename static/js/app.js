document.documentElement.setAttribute("data-theme", "dark");

function toggleTheme() {

    const currentTheme =
        document.documentElement.getAttribute("data-theme");

    document.documentElement.setAttribute(
        "data-theme",
        currentTheme === "light" ? "dark" : "light"
    );
}


function loadGoodSample() {

    document.getElementById("emailInput").value =
`From: jane.doe@yourcompany.com
Subject: Quarterly Team Meeting

Hi Team,

This is a reminder that our quarterly planning meeting
is scheduled for next Monday at 10am in the boardroom.

Agenda items are attached. Please review before the
meeting.

No action or login is required for this email.

Best regards,
Jane Doe
Project Manager, YourCompany`;

    document.getElementById("results").innerHTML =
        "No analysis yet.";
}

function loadBadSample() {

    document.getElementById("emailInput").value =
`From: support@paypa1-secure.com
Subject: Urgent Verify Account

Your account will be disabled within 24 hours.

Click http://paypa1-login.com

and enter credentials.`;

    document.getElementById("results").innerHTML =
        "No analysis yet.";
}


function resetForm() {

    document.getElementById("emailInput").value = "";

    document.getElementById("results").innerHTML =
        "No analysis yet.";
}


async function analyzeEmail() {

    const email =
        document.getElementById("emailInput").value;

    if (email.trim() === "") {

        document.getElementById("results").innerHTML =
            "<p>Please paste an email before analyzing.</p>";

        return;
    }

    try {

        const response = await fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email
            })
        });

        const result = await response.json();

        let badgeClass = "badge-good";

        if (result.verdict === "Suspicious") {
            badgeClass = "badge-warn";
        } else if (result.verdict === "Likely Phishing") {
            badgeClass = "badge-bad";
        }

        let html = `
            <div class="badge ${badgeClass}">${result.verdict}</div>
            <div class="score">${result.score}%</div>
        `;

        if (result.flags && result.flags.length > 0) {

            result.flags.forEach(flag => {

                html += `
                    <div class="flag">
                        ${flag}
                    </div>
                `;
            });
        }

        html += `
            <p>
                <strong>Recommendation:</strong>
                Do not click links or provide credentials.
                Report suspicious emails to IT Security.
            </p>
        `;

        html += `
            <button
                class="secondary"
                onclick="askCoach()">
                🎓 Ask the Awareness Coach
            </button>
        `;

        if (result.score >= 60) {

            html += `
                <button
                    class="primary"
                    onclick="reportEmail()">
                    🚨 Report To IT Security
                </button>
            `;
        }

        document.getElementById("results").innerHTML = html;

    }
    catch (error) {

        console.error(error);

        document.getElementById("results").innerHTML =
            "<div class='flag'>Error connecting to server.</div>";
    }
}


async function askCoach() {

    const email =
        document.getElementById("emailInput").value;

    if (email.trim() === "") {
        alert("Please paste an email before asking the coach.");
        return;
    }

    const resultsDiv = document.getElementById("results");

    resultsDiv.innerHTML += `
        <div class="success-box">
            <h3>🎓 Awareness Coach</h3>
            <p>Generating a question... (this uses AI and may take a moment)</p>
        </div>
    `;

    try {

        const response = await fetch("/coach", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email
            })
        });

        const result = await response.json();

        if (result.error) {
            resultsDiv.innerHTML += `
                <div class="flag">
                    ${result.error}
                </div>
            `;
            return;
        }

        let html = `
            <div class="success-box">
                <h3>🎓 Awareness Coach</h3>
                <p><strong>${result.question}</strong></p>
            </div>
        `;

        result.options.forEach((option, index) => {
            html += `
                <div
                    class="coach-option"
                    id="coach-opt-${index}"
                    onclick="selectCoachAnswer(${index}, ${result.correct_index})">
                    ${option}
                </div>
            `;
        });

        html += `
            <div id="coach-feedback" class="coach-feedback"></div>
        `;

        resultsDiv.innerHTML += html;

    }
    catch (error) {

        console.error(error);

        resultsDiv.innerHTML += `
            <div class="flag">Error connecting to the awareness coach.</div>
        `;
    }
}


function selectCoachAnswer(selected, correct) {

    const feedback = document.getElementById("coach-feedback");

    if (selected === correct) {

        document.getElementById(`coach-opt-${selected}`).classList.add("correct");

        feedback.innerHTML = `
            <div class="success-box">
                <h3>✅ Correct!</h3>
            </div>
        `;

    } else {

        document.getElementById(`coach-opt-${selected}`).classList.add("wrong");
        document.getElementById(`coach-opt-${correct}`).classList.add("correct");

        feedback.innerHTML = `
            <div class="success-box">
                <h3>❌ Not quite.</h3>
                <p>The correct answer is highlighted green.</p>
            </div>
        `;
    }
}


async function reportEmail() {

    const email =
        document.getElementById("emailInput").value;

    try {

        const response = await fetch("/report", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email
            })
        });

        const result = await response.json();

        document.getElementById("results").innerHTML += `
            <div class="success-box">
                <h3>✅ Email Reported</h3>
                <p>${result.message}</p>
            </div>
        `;
    }
    catch (error) {

        console.error(error);

        alert("Unable to report email.");
    }
}