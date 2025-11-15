// Government User Dashboard JavaScript

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        button.classList.add('active');
        const tabId = button.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
        
        if (tabId === 'inventory') loadInventory();
        if (tabId === 'reports') loadReports();
        if (tabId === 'stations') loadStations();
    });
});

// Add Supplies
document.getElementById('addSupplyForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        supply: document.getElementById('supplyType').value,
        quantity: document.getElementById('supplyQty').value
    };
    
    const response = await fetch('/api/add-supplies', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    
    if (response.ok) {
        alert('✅ Supplies added successfully!');
        document.getElementById('addSupplyForm').reset();
        loadInventory();
    } else {
        alert('❌ Failed to add supplies.');
    }
});

// Load Inventory
async function loadInventory() {
    const response = await fetch('/api/inventory');
    const supplies = await response.json();
    
    const container = document.getElementById('inventoryList');
    
    if (supplies.length === 0) {
        container.innerHTML = '<p>No supplies in inventory.</p>';
        return;
    }
    
    container.innerHTML = supplies.map(supply => `
        <div class="inventory-card">
            <div>
                <h4>${supply.name.toUpperCase()}</h4>
                <p>Quantity: <strong>${supply.quantity} ${supply.unit || 'units'}</strong></p>
            </div>
        </div>
    `).join('');
}

// Load Reports
async function loadReports() {
    const response = await fetch('/api/reports');
    const reports = await response.json();
    
    const container = document.getElementById('reportsList');
    
    if (reports.length === 0) {
        container.innerHTML = '<p>No reports filed yet.</p>';
        return;
    }
    
    container.innerHTML = reports.map((report, index) => `
        <div class="report-card">
            <div>
                <h4>📋 ${report.disaster_type.toUpperCase()}</h4>
                <p><strong>Reporter:</strong> ${report.name}</p>
                <p><strong>Time:</strong> ${report.timestamp}</p>
                <p><strong>Details:</strong> ${report.details}</p>
            </div>
            <div class="card-actions">
                <button class="btn btn-danger btn-small" onclick="deleteReport(${index + 1})">Delete</button>
            </div>
        </div>
    `).join('');
}

// Delete Report
async function deleteReport(reportId) {
    if (!confirm('Are you sure you want to delete this report?')) return;
    
    const response = await fetch(`/api/delete-report/${reportId}`, {
        method: 'POST'
    });
    
    if (response.ok) {
        alert('✅ Report deleted.');
        loadReports();
    } else {
        alert('❌ Failed to delete report.');
    }
}

// Load Stations
async function loadStations() {
    const response = await fetch('/api/stations');
    const stations = await response.json();
    
    const container = document.getElementById('stationsList');
    
    if (stations.length === 0) {
        container.innerHTML = '<p>No aid centres registered.</p>';
        return;
    }
    
    container.innerHTML = stations.map(station => `
        <div class="station-card">
            <div>
                <h4>🏢 ${station}</h4>
                <p>Registered aid centre</p>
            </div>
            <div class="card-actions">
                <button class="btn btn-danger btn-small" onclick="deleteStation('${station}')">Delete</button>
            </div>
        </div>
    `).join('');
}

// Add Station
document.getElementById('addStationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        name: document.getElementById('stationName').value
    };
    
    const response = await fetch('/api/add-station', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    
    if (response.ok) {
        alert('✅ Aid centre added successfully!');
        document.getElementById('addStationForm').reset();
        loadStations();
    } else {
        const error = await response.json();
        alert(`❌ ${error.message}`);
    }
});

// Delete Station
async function deleteStation(name) {
    if (!confirm(`Delete "${name}"?`)) return;
    
    const response = await fetch(`/api/delete-station/${encodeURIComponent(name)}`, {
        method: 'POST'
    });
    
    if (response.ok) {
        alert('✅ Centre deleted.');
        loadStations();
    } else {
        alert('❌ Failed to delete centre.');
    }
}

// Load initial content
loadInventory();
