const API_URL = '/api';

// DOM Elements
const sidebar = document.getElementById('sidebar');
const toggleSidebarBtn = document.getElementById('toggle-sidebar');
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const uploadBtn = document.getElementById('upload-btn');
const languageSelect = document.getElementById('language');
const modelSelect = document.getElementById('model');
const customPromptInput = document.getElementById('custom-prompt');
const uploadClientSelect = document.getElementById('upload-client');
const clientFilterSelect = document.getElementById('client-filter');
const jobsList = document.getElementById('jobs-list');
const clearHistoryBtn = document.getElementById('clear-history-btn');
const settingsToggle = document.getElementById('settings-toggle');
const toastContainer = document.getElementById('toast-container');

// Modals
const resultModal = document.getElementById('result-modal');
const clientModal = document.getElementById('client-modal');
const settingsModal = document.getElementById('settings-modal');
const addClientBtn = document.getElementById('add-client-btn');
const saveClientBtn = document.getElementById('save-client-btn');
const newClientNameInput = document.getElementById('new-client-name');
const closeModalBtns = document.querySelectorAll('.close-modal, .close-modal-client, .close-modal-settings, .modal-backdrop');

// Modal action buttons
const editBtn = document.getElementById('edit-btn');
const deleteJobBtn = document.getElementById('delete-job-btn');

// State
let selectedFile = null;
let jobs = [];
let clients = [];
let currentJobId = null;
let isEditMode = false;

// --- Initialization ---
init();

function init() {
    fetchClients();
    fetchJobs();
    startPolling();
    setupEventListeners();
}

function setupEventListeners() {
    // Sidebar toggle button
    toggleSidebarBtn.addEventListener('click', () => {
        const isCollapsed = sidebar.classList.contains('collapsed');
        if (isCollapsed) {
            sidebar.classList.remove('collapsed');
            // Keep the same icon, just toggle sidebar
        } else {
            sidebar.classList.add('collapsed');
        }
    });

    // Sidebar logo icon - reopen when collapsed
    const logoIcon = document.querySelector('.logo-icon');
    logoIcon.addEventListener('click', () => {
        if (sidebar.classList.contains('collapsed')) {
            sidebar.classList.remove('collapsed');
        }
    });

    // Settings
    settingsToggle.addEventListener('click', () => {
        settingsModal.classList.remove('hidden');
    });

    // File Upload
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); });
    dropZone.addEventListener('dragleave', () => { dropZone.classList.remove('drag-over'); });
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) handleFileSelect(e.dataTransfer.files[0]);
    });
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFileSelect(e.target.files[0]);
    });

    uploadBtn.addEventListener('click', uploadFile);

    // Clients
    addClientBtn.addEventListener('click', () => clientModal.classList.remove('hidden'));
    saveClientBtn.addEventListener('click', createClient);
    clientFilterSelect.addEventListener('change', () => fetchJobs(clientFilterSelect.value));

    // History
    clearHistoryBtn.addEventListener('click', clearHistory);

    // Modal actions
    editBtn.addEventListener('click', toggleEditMode);
    deleteJobBtn.addEventListener('click', deleteCurrentJob);

    // Modals
    closeModalBtns.forEach(btn => btn.addEventListener('click', () => {
        resultModal.classList.add('hidden');
        clientModal.classList.add('hidden');
        settingsModal.classList.add('hidden');
        if (isEditMode) toggleEditMode(); // Exit edit mode when closing
    }));

    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            e.target.classList.add('active');
            document.getElementById(`${e.target.dataset.tab}-content`).classList.add('active');
        });
    });
}

// --- Utility Functions ---

function groupJobsByDate(jobs) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const thisWeek = new Date(today);
    thisWeek.setDate(thisWeek.getDate() - 7);

    const groups = {
        'Today': [],
        'Yesterday': [],
        'This Week': [],
        'Last Week': [],
        'Older': []
    };

    jobs.forEach(job => {
        const jobDate = new Date(job.created_at);
        const jobDay = new Date(jobDate.getFullYear(), jobDate.getMonth(), jobDate.getDate());

        if (jobDay.getTime() === today.getTime()) {
            groups['Today'].push(job);
        } else if (jobDay.getTime() === yesterday.getTime()) {
            groups['Yesterday'].push(job);
        } else if (jobDate >= thisWeek) {
            groups['This Week'].push(job);
        } else if (jobDate >= new Date(thisWeek.getTime() - 7 * 24 * 60 * 60 * 1000)) {
            groups['Last Week'].push(job);
        } else {
            groups['Older'].push(job);
        }
    });

    return groups;
}

// --- Logic ---

function addActivity(message, type = 'info') {
    const activityItems = document.getElementById('activity-items');
    const item = document.createElement('div');
    item.className = `activity-item ${type}`;

    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

    item.innerHTML = `
        <span class="activity-dot"></span>
        <span class="activity-text">${message}</span>
        <span style="font-size: 0.75rem; color: var(--text-muted);">${timeStr}</span>
    `;

    activityItems.insertBefore(item, activityItems.firstChild);

    // Keep only last 10 items
    while (activityItems.children.length > 10) {
        activityItems.removeChild(activityItems.lastChild);
    }
}

function handleFileSelect(file) {
    selectedFile = file;
    fileInfo.textContent = `${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)`;
    uploadBtn.disabled = false;
    addActivity(`File selected: ${file.name}`, 'info');
}

async function uploadFile() {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('language', languageSelect.value);
    formData.append('model', modelSelect.value);
    if (customPromptInput.value.trim()) formData.append('custom_prompt', customPromptInput.value.trim());
    if (uploadClientSelect.value) formData.append('client_id', uploadClientSelect.value);

    setUploadLoading(true);
    addActivity('Uploading file...', 'processing');

    try {
        const response = await fetch(`${API_URL}/transcribe`, { method: 'POST', body: formData });
        if (!response.ok) throw new Error('Upload failed');

        const job = await response.json();
        jobs.unshift(job);
        renderJobs();
        addActivity('Upload successful! Processing started.', 'success');
        showToast('Upload successful! Processing started.', 'success');
        resetUploadForm();
    } catch (error) {
        console.error(error);
        addActivity('Error uploading file', 'error');
        showToast('Error uploading file.', 'error');
    } finally {
        setUploadLoading(false);
    }
}

function setUploadLoading(isLoading) {
    uploadBtn.disabled = isLoading;
    uploadBtn.querySelector('span').textContent = isLoading ? 'Uploading...' : 'Start Processing';
    if (isLoading) uploadBtn.querySelector('.loader').classList.remove('hidden');
    else uploadBtn.querySelector('.loader').classList.add('hidden');
}

function resetUploadForm() {
    selectedFile = null;
    fileInfo.textContent = '';
    fileInput.value = '';
    customPromptInput.value = '';
}

// --- Clients ---

async function fetchClients() {
    try {
        const response = await fetch(`${API_URL}/clients`);
        if (response.ok) {
            clients = await response.json();
            renderClientSelects();
        }
    } catch (e) { console.error(e); }
}

async function createClient() {
    const name = newClientNameInput.value.trim();
    if (!name) return;

    try {
        const response = await fetch(`${API_URL}/clients`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });

        if (response.ok) {
            const client = await response.json();
            clients.push(client);
            renderClientSelects();
            clientModal.classList.add('hidden');
            newClientNameInput.value = '';
            showToast('Client added', 'success');
        } else {
            showToast('Failed to add client', 'error');
        }
    } catch (e) {
        showToast('Error adding client', 'error');
    }
}

function renderClientSelects() {
    const options = clients.map(c => `<option value="${c.id}">${c.name}</option>`).join('');

    // Filter Select
    const currentFilter = clientFilterSelect.value;
    clientFilterSelect.innerHTML = `<option value="">All Clients</option>` + options;
    clientFilterSelect.value = currentFilter;

    // Upload Select
    uploadClientSelect.innerHTML = `<option value="">No Client</option>` + options;
}

// --- Jobs & History ---

async function fetchJobs(clientId = null) {
    let url = `${API_URL}/jobs`;
    if (clientId) url += `?client_id=${clientId}`;

    try {
        const response = await fetch(url);
        if (response.ok) {
            jobs = await response.json();
            renderJobs();
        }
    } catch (e) { console.error(e); }
}

function renderJobs() {
    jobsList.innerHTML = '';
    if (jobs.length === 0) {
        jobsList.innerHTML = '<div class="empty-state-small">No jobs</div>';
        return;
    }

    const groupedJobs = groupJobsByDate(jobs);

    Object.entries(groupedJobs).forEach(([groupName, groupJobs]) => {
        if (groupJobs.length === 0) return;

        // Create group header
        const groupHeader = document.createElement('div');
        groupHeader.className = 'job-group-header';
        groupHeader.textContent = groupName;
        jobsList.appendChild(groupHeader);

        // Create job items
        groupJobs.forEach(job => {
            const item = document.createElement('div');
            item.className = 'job-item-sidebar';
            item.onclick = () => viewResult(job.job_id);

            const statusClass = job.status;
            // Use semantic_title from API if available, otherwise fallback to filename
            const displayTitle = job.semantic_title || job.filename.replace(/\.(mp3|mp4|mpeg)$/i, '');

            item.innerHTML = `
                <h4>${displayTitle}</h4>
                <div class="job-meta-sidebar">
                    <span>${job.client_name || 'No Client'}</span>
                    <span class="status-dot ${statusClass}" title="${job.status}"></span>
                </div>
            `;
            jobsList.appendChild(item);
        });
    });
}

async function clearHistory() {
    if (!confirm('Clear all history?')) return;
    try {
        await fetch(`${API_URL}/jobs`, { method: 'DELETE' });
        jobs = [];
        renderJobs();
        showToast('History cleared', 'success');
    } catch (e) { showToast('Error clearing history', 'error'); }
}

async function deleteCurrentJob() {
    if (!currentJobId) return;
    if (!confirm('Delete this transcription?')) return;

    try {
        const response = await fetch(`${API_URL}/jobs/${currentJobId}`, { method: 'DELETE' });
        if (response.ok) {
            jobs = jobs.filter(j => j.job_id !== currentJobId);
            renderJobs();
            resultModal.classList.add('hidden');
            showToast('Transcription deleted', 'success');
        } else {
            showToast('Failed to delete', 'error');
        }
    } catch (e) {
        showToast('Error deleting', 'error');
    }
}

// --- Results & To-Do ---

window.viewResult = (jobId) => {
    currentJobId = jobId;
    const job = jobs.find(j => j.job_id === jobId);
    if (!job) return;

    if (job.status !== 'completed') {
        showToast(`Job is ${job.status}`, 'info');
        return;
    }

    const { transcription, analysis } = job.result;

    // Update modal title
    document.getElementById('modal-title').textContent = job.semantic_title || job.filename;

    // Transcription (READ-ONLY)
    document.getElementById('transcription-content').innerHTML = `<div class="content-display"><p>${transcription.replace(/\n/g, '<br>')}</p></div>`;

    // Report (EDITABLE)
    document.getElementById('report-content').innerHTML = analysis.report
        ? `<div class="editable-content" data-field="report"><p>${analysis.report.replace(/\n/g, '<br>')}</p></div>`
        : '<p>No report available</p>';

    // To-Do List (EDITABLE with add/delete)
    renderTodoList(analysis.todo_list || []);

    resultModal.classList.remove('hidden');
};

function renderTodoList(todoList) {
    const todoContainer = document.getElementById('todo-content');
    todoContainer.innerHTML = '';

    if (todoList.length > 0) {
        todoList.forEach((item, index) => {
            const text = typeof item === 'string' ? item : item.text;
            const isDone = typeof item === 'object' ? item.done : false;

            const div = document.createElement('div');
            div.className = `todo-item ${isDone ? 'done' : ''}`;
            div.dataset.index = index;

            div.innerHTML = `
                <input type="checkbox" class="todo-checkbox" ${isDone ? 'checked' : ''} 
                    onchange="toggleTodo('${currentJobId}', ${index}, this.checked)">
                <span class="todo-text" ${isEditMode ? 'contenteditable="true"' : ''}>${text}</span>
                ${isEditMode ? `<button class="delete-todo-btn" onclick="deleteTodoItem(${index})">×</button>` : ''}
            `;
            todoContainer.appendChild(div);
        });
    }

    if (isEditMode) {
        const addBtn = document.createElement('button');
        addBtn.className = 'add-todo-btn';
        addBtn.textContent = '+ Add Task';
        addBtn.onclick = addTodoItem;
        todoContainer.appendChild(addBtn);
    }

    if (todoList.length === 0 && !isEditMode) {
        todoContainer.innerHTML = '<p>No to-do items found</p>';
    }
}

window.addTodoItem = () => {
    const todoContainer = document.getElementById('todo-content');
    const addBtn = todoContainer.querySelector('.add-todo-btn');

    const newIndex = todoContainer.querySelectorAll('.todo-item').length;
    const div = document.createElement('div');
    div.className = 'todo-item edit-mode';
    div.dataset.index = newIndex;

    div.innerHTML = `
        <input type="checkbox" class="todo-checkbox">
        <span class="todo-text" contenteditable="true" placeholder="New task...">New task</span>
        <button class="delete-todo-btn" onclick="deleteTodoItem(${newIndex})">×</button>
    `;

    todoContainer.insertBefore(div, addBtn);
    div.querySelector('.todo-text').focus();
};

window.deleteTodoItem = (index) => {
    const todoContainer = document.getElementById('todo-content');
    const items = todoContainer.querySelectorAll('.todo-item');
    if (items[index]) {
        items[index].remove();
        // Re-index remaining items
        todoContainer.querySelectorAll('.todo-item').forEach((item, idx) => {
            item.dataset.index = idx;
        });
    }
};

// --- Edit Mode ---

function toggleEditMode() {
    isEditMode = !isEditMode;

    if (isEditMode) {
        editBtn.textContent = '💾'; // Save icon
        editBtn.title = 'Save';

        // Make report editable
        const reportEl = document.querySelector('[data-field="report"]');
        if (reportEl) {
            reportEl.contentEditable = 'true';
        }

        // Re-render todo list with edit controls
        const job = jobs.find(j => j.job_id === currentJobId);
        if (job && job.result.analysis.todo_list) {
            renderTodoList(job.result.analysis.todo_list);
        }

    } else {
        // Save changes
        saveEdits();
        editBtn.textContent = '✏️';
        editBtn.title = 'Edit';

        // Make report read-only
        const reportEl = document.querySelector('[data-field="report"]');
        if (reportEl) {
            reportEl.contentEditable = 'false';
        }
    }
}

async function saveEdits() {
    const reportEl = document.querySelector('[data-field="report"]');

    const updates = {};

    // Save report
    if (reportEl) {
        const newReport = reportEl.innerText.trim();
        updates.analysis_report = newReport;
    }

    // Save todo list
    const todoContainer = document.getElementById('todo-content');
    const todoItems = todoContainer.querySelectorAll('.todo-item');
    const updatedTodos = [];

    todoItems.forEach((item) => {
        const checkbox = item.querySelector('.todo-checkbox');
        const textEl = item.querySelector('.todo-text');
        const text = textEl.innerText.trim();

        if (text) { // Only save non-empty todos
            updatedTodos.push({
                text: text,
                done: checkbox.checked
            });
        }
    });

    if (updatedTodos.length > 0) {
        updates.analysis_todo = updatedTodos;
    }

    try {
        const response = await fetch(`${API_URL}/jobs/${currentJobId}/content`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });

        if (response.ok) {
            const updatedJob = await response.json();
            // Update local state
            const idx = jobs.findIndex(j => j.job_id === currentJobId);
            if (idx !== -1) {
                jobs[idx] = updatedJob;
            }

            // Re-render todo list in read mode
            renderTodoList(updatedJob.result.analysis.todo_list || []);

            showToast('Changes saved', 'success');
        } else {
            showToast('Failed to save changes', 'error');
        }
    } catch (e) {
        console.error(e);
        showToast('Error saving changes', 'error');
    }
}

window.toggleTodo = async (jobId, index, isDone) => {
    try {
        const response = await fetch(`${API_URL}/jobs/${jobId}/todo`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ index, done: isDone })
        });

        if (response.ok) {
            const job = jobs.find(j => j.job_id === jobId);
            if (job && job.result.analysis.todo_list[index]) {
                job.result.analysis.todo_list[index].done = isDone;
                const checkboxes = document.querySelectorAll('.todo-checkbox');
                if (checkboxes[index]) {
                    const itemDiv = checkboxes[index].closest('.todo-item');
                    if (isDone) itemDiv.classList.add('done');
                    else itemDiv.classList.remove('done');
                }
            }
        } else {
            showToast('Failed to update status', 'error');
        }
    } catch (e) {
        console.error(e);
        showToast('Error updating status', 'error');
    }
};

// --- Polling ---

function startPolling() {
    setInterval(async () => {
        const activeJobs = jobs.filter(j => j.status === 'queued' || j.status === 'processing');
        if (activeJobs.length === 0) return;

        for (const job of activeJobs) {
            try {
                const response = await fetch(`${API_URL}/status/${job.job_id}`);
                if (response.ok) {
                    const updatedJob = await response.json();
                    if (updatedJob.status !== job.status || updatedJob.status === 'completed') {
                        const idx = jobs.findIndex(j => j.job_id === job.job_id);
                        if (idx !== -1) {
                            jobs[idx] = updatedJob;
                            renderJobs();
                            if (updatedJob.status === 'completed') {
                                const title = updatedJob.semantic_title || updatedJob.filename;
                                addActivity(`Job completed: ${title}`, 'success');
                                showToast(`Job ${title} completed`, 'success');
                            } else if (updatedJob.status === 'error') {
                                const title = updatedJob.semantic_title || updatedJob.filename;
                                addActivity(`Job failed: ${title}`, 'error');
                            } else if (updatedJob.status === 'processing') {
                                const title = updatedJob.semantic_title || updatedJob.filename;
                                addActivity(`Processing: ${title}`, 'processing');
                            }
                        }
                    }
                }
            } catch (e) { console.error('Polling error', e); }
        }
    }, 3000);
}

// --- Utilities ---

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
