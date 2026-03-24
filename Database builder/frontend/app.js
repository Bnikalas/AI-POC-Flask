const API_BASE = "http://localhost:5000/api";
let currentState = {
    file: null,
    fileAnalysis: null,
    selectedDb: null,
    credentials: {},
    schema: null
};

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    setupFileUpload();
    loadDatabases();
});

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
            handleFileUpload(files[0]);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

async function handleFileUpload(file) {
    if (!file.name.match(/\.(csv|parquet)$/i)) {
        showToast("Please upload a CSV or Parquet file", "error");
        return;
    }

    showLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            currentState.file = file;
            currentState.fileAnalysis = data.analysis;
            displayFileAnalysis(data);
            showToast("File uploaded successfully", "success");
        } else {
            showToast(data.error || "Upload failed", "error");
        }
    } catch (error) {
        showToast("Upload error: " + error.message, "error");
    } finally {
        showLoading(false);
    }
}

function displayFileAnalysis(data) {
    const analysisDiv = document.getElementById("file-analysis");
    const resultsDiv = document.getElementById("analysis-results");

    let html = `
        <div class="analysis-item">
            <div class="analysis-label">File Name</div>
            <div class="analysis-value">${data.filename}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Total Rows</div>
            <div class="analysis-value">${data.analysis.row_count}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Total Columns</div>
            <div class="analysis-value">${data.analysis.column_count}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Columns</div>
            <div class="analysis-value">
                <ul style="margin-left: 20px;">
    `;

    data.analysis.columns.forEach(col => {
        html += `
            <li>
                <strong>${col.name}</strong> (${col.dtype}) - 
                ${col.unique_count} unique values, 
                ${col.null_count} nulls
            </li>
        `;
    });

    // Get potential keys safely
    const primaryKeys = data.analysis.potential_keys && data.analysis.potential_keys.primary_key_candidates 
        ? data.analysis.potential_keys.primary_key_candidates.join(", ") 
        : "None";
    const foreignKeys = data.analysis.potential_keys && data.analysis.potential_keys.foreign_key_candidates 
        ? data.analysis.potential_keys.foreign_key_candidates.join(", ") 
        : "None";

    html += `
                </ul>
            </div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Potential Keys</div>
            <div class="analysis-value">
                <strong>Primary Key Candidates:</strong> ${primaryKeys}<br>
                <strong>Foreign Key Candidates:</strong> ${foreignKeys}
            </div>
        </div>
    `;

    resultsDiv.innerHTML = html;
    analysisDiv.classList.remove("hidden");
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
            { name: "access_key", label: "AWS Access Key", type: "password" },
            { name: "secret_key", label: "AWS Secret Key", type: "password" },
            { name: "region", label: "AWS Region", type: "text", value: "us-east-1" },
            { name: "output_location", label: "S3 Output Location", type: "text", placeholder: "s3://bucket/path" }
        ],
        snowflake: [
            { name: "account", label: "Account Identifier", type: "text" },
            { name: "username", label: "Username", type: "text" },
            { name: "password", label: "Password", type: "password" },
            { name: "warehouse", label: "Warehouse", type: "text" },
            { name: "database", label: "Database", type: "text" }
        ],
        sqlserver: [
            { name: "server", label: "Server", type: "text" },
            { name: "database", label: "Database", type: "text" },
            { name: "username", label: "Username", type: "text" },
            { name: "password", label: "Password", type: "password" }
        ],
        postgres: [
            { name: "host", label: "Host", type: "text" },
            { name: "port", label: "Port", type: "text", value: "5432" },
            { name: "database", label: "Database", type: "text" },
            { name: "username", label: "Username", type: "text" },
            { name: "password", label: "Password", type: "password" }
        ],
        mysql: [
            { name: "host", label: "Host", type: "text" },
            { name: "port", label: "Port", type: "text", value: "3306" },
            { name: "database", label: "Database", type: "text" },
            { name: "username", label: "Username", type: "text" },
            { name: "password", label: "Password", type: "password" }
        ]
    };

    const fields = credentialFields[dbType] || [];
    fields.forEach(field => {
        html += `
            <div class="form-group">
                <label for="cred-${field.name}">${field.label}</label>
                <input 
                    type="${field.type}" 
                    id="cred-${field.name}" 
                    placeholder="${field.placeholder || ""}"
                    value="${field.value || ""}"
                >
            </div>
        `;
    });

    form.innerHTML = html;
}

// Schema Design
async function designSchema() {
    if (!currentState.fileAnalysis) {
        showToast("Please upload a file first", "error");
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
        const response = await fetch(`${API_BASE}/design-schema`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                file_analysis: currentState.fileAnalysis,
                openrouter_key: openrouterKey,
                model: model
            })
        });

        const data = await response.json();

        if (response.ok) {
            currentState.schema = data.schema;
            displaySchema(data.schema);
            showToast("Schema designed successfully", "success");
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
    content.textContent = JSON.stringify(schema, null, 2);
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
                schema: currentState.schema,
                ddl_statements: generateDDL(currentState.schema)
            })
        });

        const data = await response.json();

        if (response.ok) {
            displayDeploymentStatus("✅ Schema deployed successfully!");
            showToast("Deployment successful", "success");
        } else {
            displayDeploymentStatus("❌ " + (data.error || "Deployment failed"));
            showToast(data.error || "Deployment failed", "error");
        }
    } catch (error) {
        displayDeploymentStatus("❌ Error: " + error.message);
        showToast("Error: " + error.message, "error");
    } finally {
        showLoading(false);
    }
}

function generateDDL(schema) {
    // Simple DDL generation - expand based on your schema structure
    const ddl = [];
    if (schema.tables) {
        schema.tables.forEach(table => {
            ddl.push(`CREATE TABLE ${table.name} (...)`);
        });
    }
    return ddl;
}

function displayDeploymentStatus(message) {
    const status = document.getElementById("deployment-status");
    const content = document.getElementById("status-content");
    content.innerHTML = `<p>${message}</p>`;
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
    }, 3000);
}
