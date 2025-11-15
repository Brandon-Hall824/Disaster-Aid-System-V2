// Non-Government User Dashboard JavaScript

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        button.classList.add('active');
        const tabId = button.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
        
        if (tabId === 'request') loadSupplies();
        if (tabId === 'stations') loadStations();
        if (tabId === 'mental') loadMentalHealth();
    });
});

// File Disaster Report
document.getElementById('reportForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        disaster_type: document.getElementById('disasterType').value,
        details: document.getElementById('details').value,
        address: document.getElementById('address').value,
        city: document.getElementById('city').value,
        country: document.getElementById('country').value
    };
    
    const response = await fetch('/api/file-report', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    
    if (response.ok) {
        alert('✅ Report filed successfully!');
        document.getElementById('reportForm').reset();
    } else {
        alert('❌ Failed to file report. Please try again.');
    }
});

// Load Available Supplies
async function loadSupplies() {
    const response = await fetch('/api/available-supplies');
    const supplies = await response.json();
    
    const container = document.getElementById('suppliesList');
    
    if (supplies.length === 0) {
        container.innerHTML = '<p>No supplies available at this time.</p>';
        return;
    }
    
    container.innerHTML = supplies.map(supply => `
        <div class="supply-card">
            <div>
                <h4>${supply.name.toUpperCase()}</h4>
                <p>Available: <strong>${supply.quantity} ${supply.unit || 'units'}</strong></p>
            </div>
            <div>
                <input type="number" id="qty-${supply.name}" min="1" max="${supply.quantity}" value="1" style="width: 80px; padding: 8px;">
                <button class="btn btn-primary" onclick="requestSupply('${supply.name}', ${supply.quantity})">Request</button>
            </div>
        </div>
    `).join('');
}

// Request a Supply
async function requestSupply(supply, maxQty) {
    const qtyInput = document.getElementById(`qty-${supply}`);
    const quantity = parseInt(qtyInput.value);
    
    if (quantity <= 0 || quantity > maxQty) {
        alert(`❌ Please enter a valid quantity (1-${maxQty}).`);
        return;
    }
    
    const response = await fetch('/api/request-aid', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({supply, quantity})
    });
    
    if (response.ok) {
        const result = await response.json();
        alert(`✅ ${result.message}`);
        loadSupplies();
    } else {
        const error = await response.json();
        alert(`❌ ${error.message}`);
    }
}

// Load Help Stations
async function loadStations() {
    const response = await fetch('/api/list-stations');
    const stations = await response.json();
    
    const container = document.getElementById('stationsList');
    
    if (stations.length === 0) {
        container.innerHTML = '<p>No help stations registered yet.</p>';
        return;
    }
    
    container.innerHTML = stations.map(station => `
        <div class="station-card">
            <div>
                <h4>🏢 ${station}</h4>
                <p>Available to provide assistance</p>
            </div>
        </div>
    `).join('');
}

// Load Mental Health Support
async function loadMentalHealth() {
    const response = await fetch('/api/mental-health/check');
    const status = await response.json();
    
    const container = document.getElementById('mentalContent');
    
    if (!status.available) {
        container.innerHTML = '<p>Mental health support is not available at this time.</p>';
        return;
    }
    
    if (!status.configured) {
        container.innerHTML = `
            <div class="mental-config">
                <h4>🔧 Configure Mental Health AI</h4>
                <p>To use mental health support, please provide your OpenAI API key:</p>
                <form id="configForm" style="margin-top: 15px;">
                    <div class="form-group">
                        <label for="apiKey">OpenAI API Key:</label>
                        <input type="password" id="apiKey" placeholder="sk-..." required>
                    </div>
                    <button type="submit" class="btn btn-primary">Configure AI</button>
                </form>
            </div>
        `;
        
        document.getElementById('configForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const api_key = document.getElementById('apiKey').value;
            
            const response = await fetch('/api/mental-health/configure', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({api_key})
            });
            
            if (response.ok) {
                alert('✅ AI configured successfully!');
                loadMentalHealth();
            } else {
                const error = await response.json();
                alert(`❌ ${error.message}`);
            }
        });
    } else {
        container.innerHTML = `
            <div class="chat-container" id="chatBox"></div>
            <div class="chat-input-group">
                <input type="text" id="messageInput" placeholder="Share how you're feeling...">
                <button class="btn btn-primary" onclick="sendMentalMessage()">Send</button>
            </div>
        `;
        
        window.sendMentalMessage = async function() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            const chatBox = document.getElementById('chatBox');
            chatBox.innerHTML += `<div class="chat-message user">${message}</div>`;
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;
            
            const response = await fetch('/api/mental-health/message', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message})
            });
            
            const result = await response.json();
            chatBox.innerHTML += `<div class="chat-message bot">${result.message}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        };
    }
}

// Load initial content
loadSupplies();
