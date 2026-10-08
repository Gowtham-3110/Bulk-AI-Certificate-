document.addEventListener("DOMContentLoaded", () => {
    // Tab switching
    const navItems = document.querySelectorAll(".nav-item[data-tab]");
    const tabContents = document.querySelectorAll(".tab-content");

    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const targetId = item.getAttribute("data-tab");
            navItems.forEach(n => n.classList.remove("active"));
            tabContents.forEach(t => t.classList.remove("active"));

            item.classList.add("active");
            document.getElementById(targetId).classList.add("active");

            if (targetId === "tab-jobs") {
                loadJobsList();
            }
        });
    });

    // Default issue date to today
    const issueDateInput = document.getElementById("issue_date");
    if (issueDateInput) {
        issueDateInput.value = new Date().toISOString().split("T")[0];
    }

    // Recipients Table State
    const recipientsTbody = document.getElementById("recipients-tbody");
    const recipientCountSpan = document.getElementById("recipient-count");

    let recipients = [
        { name: "Alice Johnson", email: "alice.j@example.com", grade: "Honors (98%)" },
        { name: "Bob Martinez", email: "bob.m@example.com", grade: "Distinction" },
        { name: "Carol Davis", email: "carol.d@example.com", grade: "Completed" }
    ];

    function renderRecipients() {
        recipientsTbody.innerHTML = "";
        recipients.forEach((r, idx) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${idx + 1}</td>
                <td><input type="text" class="input-r-name" data-idx="${idx}" value="${escapeHtml(r.name)}" placeholder="Full Name" required></td>
                <td><input type="email" class="input-r-email" data-idx="${idx}" value="${escapeHtml(r.email)}" placeholder="email@domain.com" required></td>
                <td><input type="text" class="input-r-grade" data-idx="${idx}" value="${escapeHtml(r.grade || '')}" placeholder="Optional info"></td>
                <td><button type="button" class="btn btn-sm btn-danger btn-remove-r" data-idx="${idx}">✕</button></td>
            `;
            recipientsTbody.appendChild(tr);
        });
        recipientCountSpan.textContent = recipients.length;

        // Attach change listeners
        document.querySelectorAll(".input-r-name").forEach(inp => {
            inp.addEventListener("input", (e) => {
                const i = parseInt(e.target.dataset.idx, 10);
                recipients[i].name = e.target.value;
            });
        });
        document.querySelectorAll(".input-r-email").forEach(inp => {
            inp.addEventListener("input", (e) => {
                const i = parseInt(e.target.dataset.idx, 10);
                recipients[i].email = e.target.value;
            });
        });
        document.querySelectorAll(".input-r-grade").forEach(inp => {
            inp.addEventListener("input", (e) => {
                const i = parseInt(e.target.dataset.idx, 10);
                recipients[i].grade = e.target.value;
            });
        });
        document.querySelectorAll(".btn-remove-r").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const i = parseInt(e.target.dataset.idx, 10);
                recipients.splice(i, 1);
                renderRecipients();
            });
        });
    }

    renderRecipients();

    document.getElementById("btn-add-recipient").addEventListener("click", () => {
        recipients.push({ name: "", email: "", grade: "" });
        renderRecipients();
    });

    // Sample buttons
    document.getElementById("btn-load-sample").addEventListener("click", () => {
        recipients = [
            { name: "Sophia Chen", email: "sophia.chen@example.com", grade: "Grade: A+" },
            { name: "Marcus Brody", email: "marcus.brody@example.com", grade: "Grade: A" },
            { name: "Emily Watson", email: "emily.watson@example.com", grade: "Grade: A+" },
            { name: "Devon Vance", email: "devon.vance@example.com", grade: "Grade: B+" },
            { name: "Priya Sharma", email: "priya.sharma@example.com", grade: "Grade: A+" }
        ];
        renderRecipients();
        showToast("Loaded 5 valid recipients.", "info");
    });

    document.getElementById("btn-load-mixed").addEventListener("click", () => {
        recipients = [
            { name: "Dr. Gregory House", email: "greg.house@princeton.edu", grade: "Valid Entry" },
            { name: "__FAIL__ Corrupted Certificate Test", email: "fail.test@example.com", grade: "Simulated Runtime Error" },
            { name: "Lisa Cuddy", email: "lisa.cuddy@princeton.edu", grade: "Valid Entry" },
            { name: "James Wilson", email: "wilson@princeton.edu", grade: "Valid Entry" }
        ];
        renderRecipients();
        showToast("Loaded mixed batch with a simulated failure recipient to demonstrate error isolation.", "info");
    });

    // Job Form Submission
    const jobForm = document.getElementById("job-form");
    const btnSubmitJob = document.getElementById("btn-submit-job");

    jobForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        if (recipients.length === 0) {
            showToast("Please add at least one recipient.", "error");
            return;
        }

        const payloadRecipients = recipients.map(r => ({
            name: r.name.trim(),
            email: r.email.trim(),
            attributes: r.grade ? { grade: r.grade.trim() } : {}
        }));

        const payload = {
            event_name: document.getElementById("event_name").value.trim(),
            issuer_name: document.getElementById("issuer_name").value.trim() || undefined,
            template_title: document.getElementById("template_title").value.trim() || undefined,
            issue_date: document.getElementById("issue_date").value || undefined,
            recipients: payloadRecipients
        };

        btnSubmitJob.disabled = true;
        btnSubmitJob.querySelector(".btn-text").style.display = "none";
        btnSubmitJob.querySelector(".btn-spinner").style.display = "inline";

        try {
            const resp = await fetch("/api/v1/jobs", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.detail ? (Array.isArray(err.detail) ? err.detail.map(d => d.msg).join(", ") : err.detail) : "Job submission failed");
            }

            const data = await resp.json();
            showToast(`Job ${data.id.substring(0, 8)} created! Processing in background...`, "success");

            // Switch to jobs monitor tab and start tracking this job
            document.querySelector(".nav-item[data-tab='tab-jobs']").click();
            pollJobDetail(data.id);
        } catch (err) {
            showToast(err.message, "error");
        } finally {
            btnSubmitJob.disabled = false;
            btnSubmitJob.querySelector(".btn-text").style.display = "inline";
            btnSubmitJob.querySelector(".btn-spinner").style.display = "none";
        }
    });

    // Jobs Monitoring
    let activePollInterval = null;
    let selectedJobId = null;

    async function loadJobsList() {
        const container = document.getElementById("jobs-list");
        try {
            const resp = await fetch("/api/v1/jobs?limit=30");
            if (!resp.ok) throw new Error("Failed to load jobs");
            const jobs = await resp.json();

            if (jobs.length === 0) {
                container.innerHTML = `<div class="empty-state">No jobs found yet. Create your first batch!</div>`;
                return;
            }

            container.innerHTML = "";
            jobs.forEach(job => {
                const div = document.createElement("div");
                div.className = `job-item ${selectedJobId === job.id ? 'selected' : ''}`;
                div.dataset.id = job.id;
                div.innerHTML = `
                    <div class="job-item-header">
                        <span class="status-pill status-${job.status}">${job.status}</span>
                        <span class="job-item-meta">${new Date(job.created_at).toLocaleTimeString()}</span>
                    </div>
                    <div class="job-item-title">${escapeHtml(job.event_name)}</div>
                    <div class="job-item-meta" style="margin-top: 0.25rem;">
                        ${job.successful_count} / ${job.total_recipients} generated • ${job.progress_percentage}%
                    </div>
                `;
                div.addEventListener("click", () => {
                    document.querySelectorAll(".job-item").forEach(j => j.classList.remove("selected"));
                    div.classList.add("selected");
                    pollJobDetail(job.id);
                });
                container.appendChild(div);
            });

            // If no job selected yet, pick the first
            if (!selectedJobId && jobs.length > 0) {
                pollJobDetail(jobs[0].id);
            }
        } catch (err) {
            container.innerHTML = `<div class="empty-state" style="color: #EF4444;">${err.message}</div>`;
        }
    }

    document.getElementById("btn-refresh-jobs").addEventListener("click", () => {
        loadJobsList();
        if (selectedJobId) {
            fetchJobDetail(selectedJobId);
        }
    });

    function pollJobDetail(jobId) {
        selectedJobId = jobId;
        if (activePollInterval) {
            clearInterval(activePollInterval);
            activePollInterval = null;
        }

        fetchJobDetail(jobId);

        // Poll every 1.5s until job is in a terminal status
        activePollInterval = setInterval(async () => {
            const isFinished = await fetchJobDetail(jobId);
            if (isFinished) {
                clearInterval(activePollInterval);
                activePollInterval = null;
                loadJobsList(); // Refresh sidebar list
            }
        }, 1500);
    }

    async function fetchJobDetail(jobId) {
        const emptyEl = document.getElementById("job-detail-empty");
        const contentEl = document.getElementById("job-detail-content");

        try {
            const resp = await fetch(`/api/v1/jobs/${jobId}`);
            if (!resp.ok) throw new Error("Could not fetch job status");
            const job = await resp.json();

            emptyEl.style.display = "none";
            contentEl.style.display = "block";

            // Status & Header
            const statusEl = document.getElementById("detail-job-status");
            statusEl.className = `status-pill status-${job.status}`;
            statusEl.textContent = job.status;

            document.getElementById("detail-job-event").textContent = job.event_name;
            document.getElementById("detail-job-meta").textContent = 
                `Job ID: ${job.id} • Issuer: ${job.issuer_name} • Date: ${job.issue_date}`;

            // Progress Bar
            document.getElementById("detail-progress-val").textContent = `${job.progress_percentage}%`;
            document.getElementById("detail-progress-fill").style.width = `${job.progress_percentage}%`;

            // Stats
            document.getElementById("stat-total").textContent = job.total_recipients;
            document.getElementById("stat-successful").textContent = job.successful_count;
            document.getElementById("stat-failed").textContent = job.failed_count;

            // Download All Button
            const downloadAllBtn = document.getElementById("btn-download-all");
            if (job.successful_count > 0) {
                downloadAllBtn.style.display = "inline-flex";
                downloadAllBtn.href = `/api/v1/jobs/${job.id}/download-all`;
            } else {
                downloadAllBtn.style.display = "none";
            }

            // Certificates Table
            const tbody = document.getElementById("detail-certs-tbody");
            tbody.innerHTML = "";

            job.certificates.forEach(c => {
                const tr = document.createElement("tr");
                const actionHtml = c.status === "SUCCESS"
                    ? `<a href="/api/v1/certificates/${c.id}/download" target="_blank" class="btn btn-sm btn-primary">📄 Download PDF</a>`
                    : `<span style="color: var(--text-muted); font-size: 0.8rem;">N/A</span>`;

                const detailInfo = c.status === "SUCCESS"
                    ? `<code>${c.certificate_code}</code>`
                    : `<span style="color: var(--status-failed);">${escapeHtml(c.error_message || 'Error occurred')}</span>`;

                tr.innerHTML = `
                    <td><strong>${escapeHtml(c.recipient_name)}</strong></td>
                    <td>${escapeHtml(c.recipient_email)}</td>
                    <td><span class="status-pill status-${c.status}">${c.status}</span></td>
                    <td>${detailInfo}</td>
                    <td>${actionHtml}</td>
                `;
                tbody.appendChild(tr);
            });

            // Return true if finished
            return job.status === "COMPLETED" || job.status === "PARTIALLY_COMPLETED" || job.status === "FAILED";
        } catch (err) {
            console.error("Error fetching job detail:", err);
            return true;
        }
    }

    // Public Verification Form
    const verifyForm = document.getElementById("verify-form");
    const verifyInput = document.getElementById("verify-code-input");
    const verifyResultBox = document.getElementById("verify-result-box");

    verifyForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const code = verifyInput.value.trim();
        if (!code) return;

        verifyResultBox.style.display = "block";
        verifyResultBox.innerHTML = `<div>Verifying credential authenticity...</div>`;

        try {
            const resp = await fetch(`/api/v1/certificates/verify/${encodeURIComponent(code)}`);
            const data = await resp.json();

            if (data.is_valid) {
                verifyResultBox.innerHTML = `
                    <div style="border-left: 4px solid var(--status-success); padding-left: 1rem;">
                        <div style="color: var(--status-success); font-weight: 700; font-size: 1.1rem; margin-bottom: 0.5rem;">
                            ✓ Verified Authentic Credential
                        </div>
                        <p><strong>Recipient:</strong> ${escapeHtml(data.recipient_name)}</p>
                        <p><strong>Course/Event:</strong> ${escapeHtml(data.event_name)}</p>
                        <p><strong>Issuing Authority:</strong> ${escapeHtml(data.issuer_name)}</p>
                        <p><strong>Issue Date:</strong> ${escapeHtml(data.issue_date)}</p>
                        <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem;">
                            Verification Code: <code>${data.certificate_code}</code>
                        </p>
                    </div>
                `;
            } else {
                verifyResultBox.innerHTML = `
                    <div style="border-left: 4px solid var(--status-failed); padding-left: 1rem;">
                        <div style="color: var(--status-failed); font-weight: 700; font-size: 1.1rem; margin-bottom: 0.5rem;">
                            ✗ Verification Failed
                        </div>
                        <p>${escapeHtml(data.message)}</p>
                    </div>
                `;
            }
        } catch (err) {
            verifyResultBox.innerHTML = `
                <div style="color: var(--status-failed);">Network error verifying credential: ${err.message}</div>
            `;
        }
    });

    // Helper: Toast notifications
    function showToast(message, type = "info") {
        const container = document.getElementById("toast-container");
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => {
            toast.remove();
        }, 4000);
    }

    // Helper: Escape HTML
    function escapeHtml(str) {
        if (!str) return "";
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
