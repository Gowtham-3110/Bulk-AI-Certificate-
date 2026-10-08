document.addEventListener("DOMContentLoaded", () => {
    // =========================================================================
    // 1. SMART THEME SYSTEM (Light & Dark Mode)
    // =========================================================================
    const htmlEl = document.documentElement;
    const themeToggleBtn = document.getElementById("theme-toggle");
    const themeIcon = document.getElementById("theme-icon");
    const themeLabel = document.getElementById("theme-label");

    // Retrieve saved theme or default to 'light' for clean executive look
    const savedTheme = localStorage.getItem("certifyfast_theme") || "light";
    applyTheme(savedTheme);

    function applyTheme(theme) {
        htmlEl.setAttribute("data-theme", theme);
        localStorage.setItem("certifyfast_theme", theme);

        if (theme === "light") {
            themeIcon.textContent = "🌙";
            themeLabel.textContent = "Dark Mode";
        } else {
            themeIcon.textContent = "☀️";
            themeLabel.textContent = "Light Mode";
        }
    }

    themeToggleBtn.addEventListener("click", () => {
        const currentTheme = htmlEl.getAttribute("data-theme") || "light";
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        applyTheme(newTheme);
    });

    // =========================================================================
    // 2. TAB SWITCHING
    // =========================================================================
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

    // Default issue date to today's date
    const issueDateInput = document.getElementById("issue_date");
    if (issueDateInput && !issueDateInput.value) {
        issueDateInput.value = new Date().toISOString().split("T")[0];
    }

    // =========================================================================
    // 3. RECIPIENTS TABLE & STATE MANAGEMENT
    // =========================================================================
    const recipientsTbody = document.getElementById("recipients-tbody");
    const recipientCountSpan = document.getElementById("recipient-count");
    const validationSummaryEl = document.getElementById("recipient-validation-summary");

    let recipients = [
        { name: "Alice Johnson", email: "alice.j@example.com", grade: "Honors (98%)" },
        { name: "Bob Martinez", email: "bob.m@example.com", grade: "Distinction" },
        { name: "Carol Davis", email: "carol.d@example.com", grade: "Completed" }
    ];

    function validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function updateValidationSummary() {
        if (recipients.length === 0) {
            validationSummaryEl.textContent = "No recipients added";
            validationSummaryEl.style.color = "var(--text-muted)";
            return;
        }

        const invalidEmails = recipients.filter(r => !validateEmail(r.email));
        if (invalidEmails.length === 0) {
            validationSummaryEl.textContent = "✓ All emails valid";
            validationSummaryEl.style.color = "var(--status-success)";
        } else {
            validationSummaryEl.textContent = `⚠ ${invalidEmails.length} invalid email(s)`;
            validationSummaryEl.style.color = "var(--status-failed)";
        }
    }

    function renderRecipients() {
        recipientsTbody.innerHTML = "";
        recipients.forEach((r, idx) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${idx + 1}</td>
                <td><input type="text" class="input-r-name" data-idx="${idx}" value="${escapeHtml(r.name)}" placeholder="Full Name" required></td>
                <td><input type="email" class="input-r-email" data-idx="${idx}" value="${escapeHtml(r.email)}" placeholder="name@domain.com" required></td>
                <td><input type="text" class="input-r-grade" data-idx="${idx}" value="${escapeHtml(r.grade || '')}" placeholder="Optional: Distinction / A+"></td>
                <td style="text-align: center;"><button type="button" class="btn btn-sm btn-danger btn-remove-r" data-idx="${idx}" title="Remove recipient">✕</button></td>
            `;
            recipientsTbody.appendChild(tr);
        });
        recipientCountSpan.textContent = recipients.length;
        updateValidationSummary();

        // Attach listeners
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
                updateValidationSummary();
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

    document.getElementById("btn-clear-recipients").addEventListener("click", () => {
        recipients = [];
        renderRecipients();
        showToast("Cleared recipients list.", "info");
    });

    // Preset data buttons
    document.getElementById("btn-load-sample").addEventListener("click", () => {
        recipients = [
            { name: "Sophia Chen", email: "sophia.chen@example.com", grade: "Grade: A+ (Honors)" },
            { name: "Marcus Brody", email: "marcus.brody@example.com", grade: "Grade: A" },
            { name: "Emily Watson", email: "emily.watson@example.com", grade: "Distinction" },
            { name: "Devon Vance", email: "devon.vance@example.com", grade: "High Pass" },
            { name: "Priya Sharma", email: "priya.sharma@example.com", grade: "Grade: A+" }
        ];
        renderRecipients();
        showToast("Loaded 5 valid recipient samples.", "info");
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

    // =========================================================================
    // 4. QUICK PASTE / CSV IMPORT MODAL
    // =========================================================================
    const bulkModal = document.getElementById("bulk-modal");
    const bulkTextarea = document.getElementById("bulk-paste-textarea");

    document.getElementById("btn-open-bulk-import").addEventListener("click", () => {
        bulkModal.style.display = "flex";
        bulkTextarea.focus();
    });

    document.getElementById("btn-close-modal").addEventListener("click", () => {
        bulkModal.style.display = "none";
    });

    document.getElementById("btn-cancel-modal").addEventListener("click", () => {
        bulkModal.style.display = "none";
    });

    document.getElementById("btn-apply-bulk").addEventListener("click", () => {
        const text = bulkTextarea.value.trim();
        if (!text) {
            showToast("Please enter at least one recipient line.", "error");
            return;
        }

        const lines = text.split("\n");
        let addedCount = 0;

        lines.forEach(line => {
            const parts = line.split(",").map(p => p.trim());
            if (parts.length >= 2 && parts[0] && parts[1]) {
                recipients.push({
                    name: parts[0],
                    email: parts[1],
                    grade: parts[2] || ""
                });
                addedCount++;
            }
        });

        if (addedCount > 0) {
            renderRecipients();
            bulkModal.style.display = "none";
            bulkTextarea.value = "";
            showToast(`Successfully imported ${addedCount} recipients.`, "success");
        } else {
            showToast("Could not parse recipient lines. Ensure 'Name, Email' format.", "error");
        }
    });

    // =========================================================================
    // 5. JOB FORM SUBMISSION & ASYNC ENQUEUING
    // =========================================================================
    const jobForm = document.getElementById("job-form");
    const btnSubmitJob = document.getElementById("btn-submit-job");

    jobForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        if (recipients.length === 0) {
            showToast("Please add at least one recipient.", "error");
            return;
        }

        // Validate recipients
        for (let i = 0; i < recipients.length; i++) {
            if (!recipients[i].name.trim()) {
                showToast(`Recipient #${i + 1} has an empty name.`, "error");
                return;
            }
            if (!validateEmail(recipients[i].email.trim())) {
                showToast(`Recipient #${i + 1} has an invalid email: "${recipients[i].email}".`, "error");
                return;
            }
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
            showToast(`Job ${data.id.substring(0, 8)} dispatched! Processing in background...`, "success");

            // Switch to Jobs tab and monitor
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

    // =========================================================================
    // 6. JOBS MONITORING & REAL-TIME POLLING
    // =========================================================================
    let activePollInterval = null;
    let selectedJobId = null;
    let currentJobCertificates = [];

    async function loadJobsList() {
        const container = document.getElementById("jobs-list");
        try {
            const resp = await fetch("/api/v1/jobs?limit=30");
            if (!resp.ok) throw new Error("Failed to load jobs");
            const jobs = await resp.json();

            if (jobs.length === 0) {
                container.innerHTML = `<div class="empty-state">No jobs found in registry. Dispatch your first batch!</div>`;
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
                    <div class="job-item-meta">
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

            if (!selectedJobId && jobs.length > 0) {
                pollJobDetail(jobs[0].id);
            }
        } catch (err) {
            container.innerHTML = `<div class="empty-state" style="color: var(--status-failed);">${err.message}</div>`;
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

        activePollInterval = setInterval(async () => {
            const isFinished = await fetchJobDetail(jobId);
            if (isFinished) {
                clearInterval(activePollInterval);
                activePollInterval = null;
                loadJobsList();
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

            // Status pill
            const statusEl = document.getElementById("detail-job-status");
            statusEl.className = `status-pill status-${job.status}`;
            statusEl.textContent = job.status;

            document.getElementById("detail-job-id-short").textContent = `ID: ${job.id.substring(0, 8)}...`;
            document.getElementById("detail-job-event").textContent = job.event_name;
            document.getElementById("detail-job-meta").textContent = 
                `Authority: ${job.issuer_name} • Issued: ${job.issue_date} • Created: ${new Date(job.created_at).toLocaleString()}`;

            // Progress bar
            document.getElementById("detail-progress-val").textContent = `${job.progress_percentage}%`;
            document.getElementById("detail-progress-fill").style.width = `${job.progress_percentage}%`;

            // Stats counters
            document.getElementById("stat-total").textContent = job.total_recipients;
            document.getElementById("stat-successful").textContent = job.successful_count;
            document.getElementById("stat-failed").textContent = job.failed_count;

            // Download All (.ZIP) Button
            const downloadAllBtn = document.getElementById("btn-download-all");
            if (job.successful_count > 0) {
                downloadAllBtn.style.display = "inline-flex";
                downloadAllBtn.href = `/api/v1/jobs/${job.id}/download-all`;
            } else {
                downloadAllBtn.style.display = "none";
            }

            // Certificates table
            currentJobCertificates = job.certificates || [];
            renderFilteredCertificates();

            return job.status === "COMPLETED" || job.status === "PARTIALLY_COMPLETED" || job.status === "FAILED";
        } catch (err) {
            console.error("Error fetching job detail:", err);
            return true;
        }
    }

    // Filter certificates in real-time
    const certSearchInput = document.getElementById("cert-search-input");
    certSearchInput.addEventListener("input", () => {
        renderFilteredCertificates();
    });

    function renderFilteredCertificates() {
        const query = certSearchInput.value.toLowerCase().trim();
        const tbody = document.getElementById("detail-certs-tbody");
        tbody.innerHTML = "";

        const filtered = currentJobCertificates.filter(c => {
            return c.recipient_name.toLowerCase().includes(query) ||
                   c.recipient_email.toLowerCase().includes(query) ||
                   c.certificate_code.toLowerCase().includes(query);
        });

        if (filtered.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">No matching recipients found.</td></tr>`;
            return;
        }

        filtered.forEach(c => {
            const tr = document.createElement("tr");

            let actionHtml = `<span style="color: var(--text-muted); font-size: 0.82rem;">None</span>`;
            if (c.status === "SUCCESS") {
                const previewUrl = c.preview_url || `/api/v1/certificates/${c.id}/preview`;
                const downloadUrl = c.download_url || `/api/v1/certificates/${c.id}/download`;
                actionHtml = `
                    <div style="display: flex; gap: 0.4rem; justify-content: center;">
                        <button type="button" class="btn btn-sm btn-action-view btn-preview-cert" data-id="${c.id}" data-name="${escapeHtml(c.recipient_name)}" data-preview-url="${previewUrl}" data-download-url="${downloadUrl}">👁️ Preview</button>
                        <a href="${downloadUrl}" download class="btn btn-sm btn-primary">📄 PDF</a>
                    </div>
                `;
            }

            const detailInfo = c.status === "SUCCESS"
                ? `<code>${c.certificate_code}</code>`
                : `<span style="color: var(--status-failed); font-weight: 500;">${escapeHtml(c.error_message || 'Rendering error')}</span>`;

            tr.innerHTML = `
                <td><strong>${escapeHtml(c.recipient_name)}</strong></td>
                <td>${escapeHtml(c.recipient_email)}</td>
                <td><span class="status-pill status-${c.status}">${c.status}</span></td>
                <td>${detailInfo}</td>
                <td style="text-align: center;">${actionHtml}</td>
            `;
            tbody.appendChild(tr);
        });

        // Attach preview modal triggers
        document.querySelectorAll(".btn-preview-cert").forEach(btn => {
            btn.addEventListener("click", () => {
                const certName = btn.dataset.name;
                const previewUrl = btn.dataset.previewUrl || `/api/v1/certificates/${btn.dataset.id}/preview`;
                const downloadUrl = btn.dataset.downloadUrl || `/api/v1/certificates/${btn.dataset.id}/download`;
                openPreviewModal(certName, previewUrl, downloadUrl);
            });
        });
    }

    // =========================================================================
    // 7. LIVE PDF CERTIFICATE PREVIEW MODAL
    // =========================================================================
    const previewModal = document.getElementById("preview-modal");
    const previewTitle = document.getElementById("preview-title");
    const previewIframe = document.getElementById("preview-iframe");
    const previewLoading = document.getElementById("preview-loading");
    const btnPreviewDownload = document.getElementById("btn-preview-download");
    const btnPreviewNewtab = document.getElementById("btn-preview-newtab");

    function closePreviewModal() {
        previewModal.style.display = "none";
        previewIframe.src = "about:blank";
        if (previewLoading) previewLoading.style.display = "none";
    }

    function openPreviewModal(recipientName, previewUrl, downloadUrl) {
        previewTitle.textContent = `Certificate Preview: ${recipientName}`;
        
        if (previewLoading) previewLoading.style.display = "flex";

        previewIframe.onload = () => {
            if (previewLoading) previewLoading.style.display = "none";
        };

        previewIframe.src = previewUrl;
        btnPreviewDownload.href = downloadUrl || previewUrl;
        if (btnPreviewNewtab) {
            btnPreviewNewtab.href = previewUrl;
        }

        previewModal.style.display = "flex";
    }

    document.getElementById("btn-close-preview").addEventListener("click", closePreviewModal);
    document.getElementById("btn-close-preview-btn").addEventListener("click", closePreviewModal);

    previewModal.addEventListener("click", (e) => {
        if (e.target === previewModal) {
            closePreviewModal();
        }
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && previewModal.style.display === "flex") {
            closePreviewModal();
        }
    });

    // =========================================================================
    // 8. PUBLIC CREDENTIAL VERIFICATION
    // =========================================================================
    const verifyForm = document.getElementById("verify-form");
    const verifyInput = document.getElementById("verify-code-input");
    const verifyResultBox = document.getElementById("verify-result-box");

    verifyForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const code = verifyInput.value.trim();
        if (!code) return;

        verifyResultBox.style.display = "block";
        verifyResultBox.innerHTML = `<div>Checking official credential registry...</div>`;

        try {
            const resp = await fetch(`/api/v1/certificates/verify/${encodeURIComponent(code)}`);
            const data = await resp.json();

            if (data.is_valid) {
                verifyResultBox.innerHTML = `
                    <div style="border-left: 4px solid var(--status-success); padding-left: 1.25rem;">
                        <div style="color: var(--status-success); font-weight: 800; font-size: 1.15rem; margin-bottom: 0.6rem;">
                            ✓ Officially Verified & Authentic Credential
                        </div>
                        <p style="margin-bottom: 0.35rem;"><strong>Recipient Name:</strong> ${escapeHtml(data.recipient_name)}</p>
                        <p style="margin-bottom: 0.35rem;"><strong>Course / Event:</strong> ${escapeHtml(data.event_name)}</p>
                        <p style="margin-bottom: 0.35rem;"><strong>Issuing Authority:</strong> ${escapeHtml(data.issuer_name)}</p>
                        <p style="margin-bottom: 0.35rem;"><strong>Issue Date:</strong> ${escapeHtml(data.issue_date)}</p>
                        <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.6rem;">
                            Cryptographic Identifier: <code>${data.certificate_code}</code>
                        </p>
                    </div>
                `;
            } else {
                verifyResultBox.innerHTML = `
                    <div style="border-left: 4px solid var(--status-failed); padding-left: 1.25rem;">
                        <div style="color: var(--status-failed); font-weight: 800; font-size: 1.15rem; margin-bottom: 0.6rem;">
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

    // =========================================================================
    // 9. TOAST NOTIFICATIONS & UTILITIES
    // =========================================================================
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
