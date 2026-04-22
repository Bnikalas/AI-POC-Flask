const API_BASE = "http://localhost:5000/api";
let currentState = {
    openrouterKey: null,
    model: null,
    files: [],  // Changed to array for multiple files
    fileAnalyses: {},  // Map of filename -> analysis
    selectedDb: null,
    credentials: {},
    schema: null,
    executionLogs: null,
    correctedSQL: null
};

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    setupFileUpload();
    loadDatabases();
    loadConfig();
    setupLLMConfig();
});

// LLM Configuration Setup
function setupLLMConfig() {
    const apiKeyInput = document.getElementById("openrouter-key");
    const modelInput = document.getElementById("model-select");
    
    apiKeyInput.addEventListener("change", () => {
        currentState.openrouterKey = apiKeyInput.value;
    });
    
    modelInput.addEventListener("change", () => {
        currentState.model = modelInput.value;
    });
}

// File Upload
function setupFileUpload() {
    const uploadArea = document.getElementById("upload-area");
    const fileInput = document.getElementById("file-upload");

    uploadArea.addEventListener("click", () => fileInput.click());

    uploadArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadArea.classList.add("dragover");
    });

    uploadArea.addEventListener("dragleave", () => {
        uploadArea.classList.remove("dragover");
    });

    uploadArea.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadArea.classList.remove("dragover");
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files);
        }
    });
}

async function handleFileUpload(files) {
    // Check if LLM is configured first
    const openrouterKey = document.getElementById("openrouter-key").value;
    const model = document.getElementById("model-select").value;
    
    if (!openrouterKey) {
        showToast("Please enter OpenRouter API key first (Step 1)", "error");
        return;
    }
    
    if (!model) {
        showToast("Please enter LLM model first (Step 1)", "error");
        return;
    }
    
    // Validate all files
    const validFiles = [];
    for (let file of files) {
        if (!file.name.match(/\.(csv|parquet)$/i)) {
            showToast(`File "${file.name}" is not CSV or Parquet`, "error");
            continue;
        }
        if (file.size > 16 * 1024 * 1024) {
            showToast(`File "${file.name}" exceeds 16MB limit`, "error");
            continue;
        }
        validFiles.push(file);
    }
    
    if (validFiles.length === 0) {
        showToast("No valid files to upload", "error");
        return;
    }
    
    // Add files to current state
    currentState.files = [...currentState.files, ...validFiles];
    currentState.openrouterKey = openrouterKey;
    currentState.model = model;
    
    // Display uploaded files
    displayUploadedFiles();
    
    // Upload and analyze each file
    for (let file of validFiles) {
        await uploadAndAnalyzeFile(file, openrouterKey, model);
    }
}

async function uploadAndAnalyzeFile(file, openrouterKey, model) {
    showLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("openrouter_key", openrouterKey);
    formData.append("model", model);

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            // Store analysis for this file
            currentState.fileAnalyses[file.name] = data.analysis;
            
            // Update file status
            updateFileStatus(file.name, "analyzed");
            
            // Display analysis tabs
            displayAnalysisTabs();
            
            // Show first file's analysis by default
            if (Object.keys(currentState.fileAnalyses).length === 1) {
                selectFileAnalysis(file.name);
            }
            
            showToast(`File "${file.name}" analyzed successfully`, "success");
        } else {
            updateFileStatus(file.name, "error");
            showToast(data.error || `Failed to analyze "${file.name}"`, "error");
        }
    } catch (error) {
        updateFileStatus(file.name, "error");
        showToast(`Upload error for "${file.name}": ${error.message}`, "error");
    } finally {
        showLoading(false);
    }
}

function displayUploadedFiles() {
    const container = document.getElementById("files-container");
    const listDiv = document.getElementById("uploaded-files-list");
    
    container.innerHTML = "";
    
    currentState.files.forEach(file => {
        const fileCard = document.createElement("div");
        fileCard.className = "file-card";
        fileCard.id = `file-card-${file.name}`;
        
        const status = currentState.fileAnalyses[file.name] ? "analyzed" : "analyzing";
        const statusClass = status === "analyzed" ? "analyzed" : "analyzing";
        const statusText = status === "analyzed" ? "✓ Analyzed" : "⏳ Analyzing...";
        
        fileCard.innerHTML = `
            <div class="file-icon">📄</div>
            <div class="file-name">${file.name}</div>
            <div class="file-size">${(file.size / 1024).toFixed(2)} KB</div>
            <div class="file-status ${statusClass}">${statusText}</div>
        `;
        
        fileCard.onclick = () => selectFileAnalysis(file.name);
        container.appendChild(fileCard);
    });
    
    listDiv.classList.remove("hidden");
}

function updateFileStatus(fileName, status) {
    const fileCard = document.getElementById(`file-card-${fileName}`);
    if (!fileCard) return;
    
    const statusEl = fileCard.querySelector(".file-status");
    if (status === "analyzed") {
        statusEl.textContent = "✓ Analyzed";
        statusEl.className = "file-status analyzed";
    } else if (status === "error") {
        statusEl.textContent = "✗ Error";
        statusEl.className = "file-status";
        statusEl.style.background = "rgba(239, 68, 68, 0.2)";
        statusEl.style.color = "var(--accent-danger)";
    }
}

function displayAnalysisTabs() {
    const tabsContainer = document.getElementById("analysis-tabs");
    const tabsDiv = document.getElementById("file-analysis-tabs");
    
    tabsContainer.innerHTML = "";
    
    Object.keys(currentState.fileAnalyses).forEach(fileName => {
        const tab = document.createElement("button");
        tab.className = "analysis-tab";
        tab.textContent = fileName;
        tab.onclick = () => selectFileAnalysis(fileName);
        tabsContainer.appendChild(tab);
    });
    
    tabsDiv.classList.remove("hidden");
}

function selectFileAnalysis(fileName) {
    // Update active tab
    document.querySelectorAll(".analysis-tab").forEach(tab => {
        tab.classList.remove("active");
        if (tab.textContent === fileName) {
            tab.classList.add("active");
        }
    });
    
    // Update file card selection
    document.querySelectorAll(".file-card").forEach(card => {
        card.classList.remove("selected");
    });
    const selectedCard = document.getElementById(`file-card-${fileName}`);
    if (selectedCard) {
        selectedCard.classList.add("selected");
    }
    
    // Display analysis
    displayFileAnalysis(fileName);
}

function displayFileAnalysis(fileName) {
    const analysis = currentState.fileAnalyses[fileName];
    if (!analysis) return;
    
    const resultsDiv = document.getElementById("analysis-results");
    
    let html = `
        <div class="analysis-item">
            <div class="analysis-label">📄 File Name</div>
            <div class="analysis-value">${fileName}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">📊 Total Columns</div>
            <div class="analysis-value">${analysis.column_count}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">🔍 Columns & Data Types</div>
            <div class="analysis-value">
                <ul>
    `;

    analysis.columns.forEach(col => {
        const isPII = col.is_pii;
        const piiClass = isPII ? ' class="pii-column"' : '';
        const piiLabel = isPII ? ' ⚠️ PII DETECTED' : '';
        html += `
            <li${piiClass}>
                <strong>${col.name}</strong> - ${col.dtype}${piiLabel}
            </li>
        `;
    });

    html += `
                </ul>
            </div>
        </div>
    `;

    resultsDiv.innerHTML = html;
}

// Database Selection
async function loadDatabases() {
    try {
        const response = await fetch(`${API_BASE}/databases`);
        const data = await response.json();

        const grid = document.getElementById("database-grid");
        grid.innerHTML = "";

        const icons = {
            athena: "☁️",
            snowflake: "❄️",
            sqlserver: "🔷",
            postgres: "🐘",
            mysql: "🐬"
        };

        Object.entries(data.databases).forEach(([key, name]) => {
            const div = document.createElement("div");
            div.className = "db-option";
            div.innerHTML = `
                <div class="db-option-icon">${icons[key] || "🗄️"}</div>
                <div class="db-option-name">${name}</div>
            `;
            div.onclick = () => selectDatabase(key, div);
            grid.appendChild(div);
        });
    } catch (error) {
        showToast("Failed to load databases", "error");
    }
}

// Load Configuration
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();
        
        // Set default model in the model input field
        const modelField = document.getElementById("model-select");
        if (modelField) {
            modelField.value = data.default_model;
            currentState.model = data.default_model;
        }
    } catch (error) {
        console.log("Could not load config, using defaults");
    }
}

function selectDatabase(dbType, element) {
    document.querySelectorAll(".db-option").forEach(el => el.classList.remove("selected"));
    element.classList.add("selected");
    currentState.selectedDb = dbType;
    document.getElementById("selected-db").value = dbType;

    // Show credentials form
    showCredentialsForm(dbType);
}

function showCredentialsForm(dbType) {
    const form = document.getElementById("credentials-form");
    let html = "";

    const credentialFields = {
        athena: [
            { name: "access_key", label: "AWS Access Key", type: "password", icon: "🔑" },
            { name: "secret_key", label: "AWS Secret Key", type: "password", icon: "🔐" },
            { name: "region", label: "AWS Region", type: "text", value: "us-east-1", icon: "🌍" },
            { name: "output_location", label: "S3 Output Location", type: "text", placeholder: "s3://bucket/path", icon: "📦" }
        ],
        snowflake: [
            { name: "account", label: "Account Identifier", type: "text", icon: "🏢" },
            { name: "username", label: "Username", type: "text", icon: "👤" },
            { name: "password", label: "Password", type: "password", icon: "🔒" },
            { name: "warehouse", label: "Warehouse", type: "text", icon: "🏭" },
            { name: "database", label: "Database", type: "text", icon: "💾" },
            { name: "schema", label: "Schema", type: "text", placeholder: "e.g., PUBLIC", icon: "📋" }
        ],
        sqlserver: [
            { name: "server", label: "Server", type: "text", icon: "🖥️" },
            { name: "database", label: "Database", type: "text", icon: "💾" },
            { name: "username", label: "Username", type: "text", icon: "👤" },
            { name: "password", label: "Password", type: "password", icon: "🔒" }
        ],
        postgres: [
            { name: "host", label: "Host", type: "text", icon: "🖥️" },
            { name: "port", label: "Port", type: "text", value: "5432", icon: "🔌" },
            { name: "database", label: "Database", type: "text", icon: "💾" },
            { name: "username", label: "Username", type: "text", icon: "👤" },
            { name: "password", label: "Password", type: "password", icon: "🔒" },
            { name: "schema", label: "Schema", type: "text", placeholder: "e.g., public", icon: "📋" }
        ],
        mysql: [
            { name: "host", label: "Host", type: "text", icon: "🖥️" },
            { name: "port", label: "Port", type: "text", value: "3306", icon: "🔌" },
            { name: "database", label: "Database", type: "text", icon: "💾" },
            { name: "username", label: "Username", type: "text", icon: "👤" },
            { name: "password", label: "Password", type: "password", icon: "🔒" }
        ]
    };

    const fields = credentialFields[dbType] || [];
    fields.forEach(field => {
        html += `
            <div class="form-group">
                <label for="cred-${field.name}">
                    <span class="label-icon">${field.icon}</span>
                    ${field.label}
                </label>
                <input 
                    type="${field.type}" 
                    id="cred-${field.name}" 
                    placeholder="${field.placeholder || ""}"
                    value="${field.value || ""}"
                    autocomplete="off"
                >
            </div>
        `;
    });

    form.innerHTML = html;
}

// Schema Design
async function designSchema() {
    if (Object.keys(currentState.fileAnalyses).length === 0) {
        showToast("Please upload at least one file first", "error");
        return;
    }
    
    if (!currentState.selectedDb) {
        showToast("Please select a database first", "error");
        return;
    }

    const openrouterKey = document.getElementById("openrouter-key").value;
    const model = document.getElementById("model-select").value;

    if (!openrouterKey) {
        showToast("Please enter OpenRouter API key", "error");
        return;
    }

    showLoading(true);

    try {
        // Get schema name from credentials
        const schemaField = document.getElementById("cred-schema");
        const schemaName = schemaField ? schemaField.value : "PUBLIC";

        // Send all file analyses to LLM
        const response = await fetch(`${API_BASE}/design-schema`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                file_analyses: currentState.fileAnalyses,  // Send all files
                openrouter_key: openrouterKey,
                model: model,
                db_type: currentState.selectedDb,
                schema_name: schemaName || "PUBLIC"
            })
        });

        const data = await response.json();

        if (response.ok) {
            currentState.schema = data.schema;
            displaySchema(data.schema);
            showToast("Schema designed successfully from all files", "success");
        } else {
            showToast(data.error || "Schema design failed", "error");
        }
    } catch (error) {
        showToast("Error: " + error.message, "error");
    } finally {
        showLoading(false);
    }
}

function displaySchema(schema) {
    const preview = document.getElementById("schema-preview");
    const content = document.getElementById("schema-content");
    
    let html = `
        <div style="margin-bottom: 20px;">
            <h4>📐 Schema Type</h4>
            <p style="color: var(--text-secondary);">${schema.schema_type}</p>
            <p style="color: var(--text-muted); margin-top: 8px;">${schema.normalization_notes || 'No normalization notes provided'}</p>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h4>📊 Tables</h4>
            <ul>
    `;
    
    if (schema.tables && schema.tables.length > 0) {
        schema.tables.forEach(table => {
            html += `<li><strong>${table.name}</strong> - ${table.description || 'No description'}</li>`;
        });
    } else {
        html += `<li>No tables defined</li>`;
    }
    
    html += `
            </ul>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h4>💻 SQL Statements</h4>
            <pre>
    `;
    
    if (schema.sql_statements && schema.sql_statements.length > 0) {
        schema.sql_statements.forEach((sql, index) => {
            const cleanedSql = sql.trim();
            html += `-- Statement ${index + 1}\n${cleanedSql};\n\n`;
        });
    } else {
        html += `No SQL statements generated`;
    }
    
    html += `
            </pre>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h4>💡 Recommendations</h4>
            <ul>
    `;
    
    if (schema.recommendations && schema.recommendations.length > 0) {
        schema.recommendations.forEach(rec => {
            const cleanedRec = rec.trim();
            html += `<li>${cleanedRec}</li>`;
        });
    } else {
        html += `<li>No additional recommendations</li>`;
    }
    
    html += `
            </ul>
        </div>
    `;
    
    content.innerHTML = html;
    preview.classList.remove("hidden");
}

// Deploy Schema
async function deploySchema() {
    if (!currentState.schema || !currentState.selectedDb) {
        showToast("Please design schema first", "error");
        return;
    }

    // Collect credentials
    const credentials = {};
    document.querySelectorAll("[id^='cred-']").forEach(input => {
        const key = input.id.replace("cred-", "");
        credentials[key] = input.value;
    });

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE}/deploy-schema`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                db_type: currentState.selectedDb,
                credentials: credentials,
                schema: currentState.schema
            })
        });

        const data = await response.json();

        // Display execution logs
        if (data.execution_logs) {
            displayExecutionLogs(data.execution_logs);
            currentState.executionLogs = data.execution_logs;
            
            // Show error correction section if there are failures
            const hasFailures = data.execution_logs.some(log => log.status === 'failed');
            if (hasFailures) {
                showErrorCorrectionSection(data.execution_logs);
            }
        }

        if (data.success) {
            displayDeploymentStatus("✅ Schema deployed successfully!");
            showToast("Deployment successful", "success");
        } else {
            displayDeploymentStatus("⚠️ " + (data.message || data.error || "Deployment completed with errors"));
            showToast(data.message || data.error || "Deployment completed with errors", "error");
        }
    } catch (error) {
        displayDeploymentStatus("❌ Error: " + error.message);
        showToast("Error: " + error.message, "error");
    } finally {
        showLoading(false);
    }
}

function displayExecutionLogs(logs) {
    const logsDiv = document.getElementById("execution-logs");
    const content = document.getElementById("logs-content");
    
    let html = `
        <table>
            <thead>
                <tr>
                    <th>Statement #</th>
                    <th>Status</th>
                    <th>SQL</th>
                    <th>Message</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    logs.forEach((log, index) => {
        const isFailed = log.status === 'failed' || log.status === 'error';
        const statusColor = log.status === 'success' ? '#10b981' : isFailed ? '#ef4444' : '#f59e0b';
        const statusIcon = log.status === 'success' ? '✓' : isFailed ? '✗' : '⏳';
        
        html += `
            <tr>
                <td>${log.statement_number}</td>
                <td style="color: ${statusColor}; font-weight: bold;">${statusIcon} ${log.status}</td>
                <td style="font-family: monospace; font-size: 0.85rem; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    ${log.sql.substring(0, 100)}${log.sql.length > 100 ? '...' : ''}
                </td>
                <td style="color: ${isFailed ? '#ef4444' : 'var(--text-secondary)'};">
                    ${log.message || log.error || '-'}
                </td>
                <td>
                    ${isFailed ? `<button class="btn-action" onclick="copyFailedStatementToCorrection(${index})" title="Copy to error correction">📋 Copy</button>` : '-'}
                </td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    content.innerHTML = html;
    logsDiv.classList.remove("hidden");
}

// Copy failed statement to error correction section
function copyFailedStatementToCorrection(logIndex) {
    const logs = currentState.executionLogs;
    if (!logs || !logs[logIndex]) {
        showToast("Log not found", "error");
        return;
    }
    
    const log = logs[logIndex];
    
    // Populate the error correction fields
    document.getElementById("failed-sql").value = log.sql;
    document.getElementById("error-message").value = log.error || log.message || '';
    
    // Show the error correction section
    const errorDiv = document.getElementById("error-correction");
    errorDiv.classList.remove("hidden");
    
    // Scroll to error correction section
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    showToast("Failed statement copied to error correction section", "success");
}

function showErrorCorrectionSection(logs) {
    const errorDiv = document.getElementById("error-correction");
    
    // Just show the section - don't auto-populate
    // User will manually copy from logs
    errorDiv.classList.remove("hidden");
    
    // Clear any previous values
    document.getElementById("failed-sql").value = '';
    document.getElementById("error-message").value = '';
    document.getElementById("corrected-sql-result").classList.add("hidden");
}

// Copy to clipboard function
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    let text = '';
    
    if (element.tagName === 'TEXTAREA') {
        text = element.value;
    } else if (element.tagName === 'PRE') {
        text = element.textContent;
    } else {
        text = element.innerText;
    }
    
    if (!text) {
        showToast("Nothing to copy", "error");
        return;
    }
    
    navigator.clipboard.writeText(text).then(() => {
        showToast("Copied to clipboard!", "success");
    }).catch(err => {
        showToast("Failed to copy", "error");
    });
}

async function fixSQLError() {
    const errorMessage = document.getElementById("error-message").value;
    const failedSQL = document.getElementById("failed-sql").value;
    
    if (!errorMessage || !failedSQL) {
        showToast("Please provide both error message and failed SQL", "error");
        return;
    }
    
    const openrouterKey = document.getElementById("openrouter-key").value;
    const model = document.getElementById("model-select").value;
    
    if (!openrouterKey) {
        showToast("Please enter OpenRouter API key", "error");
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/fix-sql`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                error_message: errorMessage,
                failed_sql: failedSQL,
                db_type: currentState.selectedDb,
                openrouter_key: openrouterKey,
                model: model
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentState.correctedSQL = data.corrected_sql;
            displayCorrectedSQL(data.corrected_sql);
            showToast("SQL corrected successfully", "success");
        } else {
            showToast(data.error || "Failed to correct SQL", "error");
        }
    } catch (error) {
        showToast("Error: " + error.message, "error");
    } finally {
        showLoading(false);
    }
}

function displayCorrectedSQL(sql) {
    const resultDiv = document.getElementById("corrected-sql-result");
    const content = document.getElementById("corrected-sql-content");
    
    content.textContent = sql;
    resultDiv.classList.remove("hidden");
}

async function redeployCorrectedSQL() {
    if (!currentState.correctedSQL) {
        showToast("No corrected SQL available", "error");
        return;
    }
    
    // Collect credentials
    const credentials = {};
    document.querySelectorAll("[id^='cred-']").forEach(input => {
        const key = input.id.replace("cred-", "");
        credentials[key] = input.value;
    });
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/deploy-schema`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                db_type: currentState.selectedDb,
                credentials: credentials,
                schema: { sql_statements: [currentState.correctedSQL] }
            })
        });
        
        const data = await response.json();
        
        // Display execution logs
        if (data.execution_logs) {
            displayExecutionLogs(data.execution_logs);
        }
        
        if (data.success) {
            displayDeploymentStatus("✅ Corrected SQL deployed successfully!");
            showToast("Corrected SQL deployed successfully", "success");
        } else {
            displayDeploymentStatus("⚠️ " + (data.message || data.error || "Deployment failed"));
            showToast(data.message || data.error || "Deployment failed", "error");
        }
    } catch (error) {
        displayDeploymentStatus("❌ Error: " + error.message);
        showToast("Error: " + error.message, "error");
    } finally {
        showLoading(false);
    }
}

function displayDeploymentStatus(message) {
    const status = document.getElementById("deployment-status");
    const content = document.getElementById("status-content");
    content.innerHTML = `<p style="font-size: 1.1rem; font-weight: 500;">${message}</p>`;
    status.classList.remove("hidden");
}

// Utilities
function showLoading(show) {
    const loading = document.getElementById("loading");
    if (show) {
        loading.classList.remove("hidden");
    } else {
        loading.classList.add("hidden");
    }
}

function showToast(message, type = "info") {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove("hidden");

    setTimeout(() => {
        toast.classList.add("hidden");
    }, 4000);
}
