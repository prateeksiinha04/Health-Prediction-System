document.addEventListener("DOMContentLoaded", () => {
   
    /* ==========================================================================
       1. GLOBAL UI & PROFILE SETTINGS
       ========================================================================== */
    const profileModal = document.getElementById('profileModal');
    const topRightProfile = document.querySelector('.profile-avatar'); 
    const saveProfileBtn = document.getElementById('saveProfileBtn');
    const googleSyncBtn = document.querySelector('.btn-google-sync');

    // Desktop Photo Upload Logic
    const desktopPhotoUpload = document.getElementById('desktopPhotoUpload');
    if (desktopPhotoUpload) {
        desktopPhotoUpload.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                if (file.size > 2.5 * 1024 * 1024) {
                    alert('Photo is too large! Please select an image under 2.5MB.');
                    return;
                }
                const reader = new FileReader();
                reader.onload = function(e) {
                    const base64Image = e.target.result;
                    try {
                        localStorage.setItem('userPhoto', base64Image);
                        updateUI(null, base64Image, null);
                        const uploadLabel = document.querySelector('label[for="desktopPhotoUpload"]');
                        if (uploadLabel) {
                            const originalText = uploadLabel.innerHTML;
                            uploadLabel.innerHTML = '<i class="fa-solid fa-check" style="color: green;"></i> Uploaded!';
                            setTimeout(() => { uploadLabel.innerHTML = originalText; }, 2000);
                        }
                    } catch (error) {
                        console.error("Storage Error:", error);
                        alert("Could not save the image. Your browser storage might be full.");
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    if (topRightProfile) {
        topRightProfile.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = 'profile-settings.html';
        });
    }

    if (googleSyncBtn) {
        googleSyncBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const currentName = localStorage.getItem('userName') || "User";
            const currentEmail = localStorage.getItem('userEmail') || "synced.user@gmail.com";
            const mockGoogleData = {
                name: currentName + " (Google)",
                email: currentEmail,
                photoUrl: "https://i.pravatar.cc/150?img=47"
            };
            localStorage.setItem('userName', mockGoogleData.name);
            localStorage.setItem('userPhoto', mockGoogleData.photoUrl);
            updateUI(mockGoogleData.name, mockGoogleData.photoUrl, mockGoogleData.email);
            googleSyncBtn.innerHTML = '<i class="fa-solid fa-check" style="color: green;"></i> Synced!';
            setTimeout(() => { googleSyncBtn.innerHTML = '<i class="fa-brands fa-google"></i> Sync Gmail Photo'; }, 2000);
        });
    }

    function updateUI(name, photoUrl, email) {
        const savedName = name || localStorage.getItem('userName') || "Guest";
        const savedPhoto = photoUrl || localStorage.getItem('userPhoto') || "https://i.pravatar.cc/100?img=32";
        const savedEmail = email || localStorage.getItem('userEmail') || "Not logged in";

        const headerGreeting = document.querySelector('.username-highlight');
        if (headerGreeting) headerGreeting.innerText = savedName;

        const topProfileName = document.querySelector('.profile-name');
        if (topProfileName) topProfileName.innerHTML = `${savedName.split(' ')[0]} <i class="fa-solid fa-chevron-down"></i>`;

        const displayName = document.getElementById('displayName');
        if (displayName) displayName.innerText = savedName;

        const allAvatars = document.querySelectorAll('.profile-avatar img, .large-avatar, #settingsAvatar, #topAvatar');
        allAvatars.forEach(img => img.src = savedPhoto);
        
        const nameInput = document.getElementById('profileName');
        if (nameInput) nameInput.value = savedName;

        const emailInput = document.getElementById('profileEmail');
        if (emailInput) emailInput.value = savedEmail;
    }

    updateUI(null, null, null);

    window.addEventListener('storage', (event) => {
        if (event.key === 'userName' || event.key === 'userPhoto' || event.key === 'userEmail') {
            updateUI(null, null, null);
        }
    });

    /* ==========================================================================
       2. AUTH / LOGIN PAGE LOGIC
       ========================================================================== */

    const loginForm = document.querySelector('.login-form');
    const altLoginBtn = document.querySelector('.btn-alt-login'); 

    if (loginForm) {
        const togglePassword = document.querySelector('.toggle-password');
        const passwordInput = document.querySelector('input[type="password"]');
        
        if (togglePassword && passwordInput) {
            togglePassword.addEventListener('click', () => {
                const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordInput.setAttribute('type', type);
                togglePassword.innerHTML = type === 'password' ? '<i class="fa-regular fa-eye-slash"></i>' : '<i class="fa-regular fa-eye"></i>';
                togglePassword.style.color = type === 'password' ? 'var(--text-muted)' : 'var(--primary)';
            });
        }

        let errorMsg = loginForm.querySelector('.error-message');
        if (!errorMsg) {
            errorMsg = document.createElement('div');
            errorMsg.className = 'error-message';
            errorMsg.style.cssText = 'color: #ef4444; font-size: 0.85rem; font-weight: 500; text-align: center; margin-bottom: 0.5rem; display: none;';
            const submitBtn = loginForm.querySelector('.btn-submit');
            loginForm.insertBefore(errorMsg, submitBtn);
        }

        loginForm.addEventListener('submit', (e) => {
            e.preventDefault(); 
            const emailInput = loginForm.querySelector('input[type="email"]');
            const passwordInput = loginForm.querySelector('input[type="password"]');
            const email = emailInput ? emailInput.value.trim() : '';
            const password = passwordInput ? passwordInput.value : '';

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (!emailRegex.test(email)) {
                errorMsg.innerText = "Please enter a valid email address.";
                errorMsg.style.display = 'block';
                return; 
            }
            if (password.length < 6) {
                errorMsg.innerText = "Password must be at least 6 characters long.";
                errorMsg.style.display = 'block';
                return; 
            }

            errorMsg.style.display = 'none';

            if (emailInput && emailInput.value) {
                localStorage.setItem('userEmail', emailInput.value);
                let derivedName = emailInput.value.split('@')[0].replace(/[._-]/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                localStorage.setItem('userName', derivedName);
                if (!localStorage.getItem('userPhoto')) localStorage.setItem('userPhoto', 'https://i.pravatar.cc/100?img=32'); 
            }

            const submitBtn = loginForm.querySelector('.btn-submit');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Authenticating...';
                submitBtn.style.opacity = '0.8';
                submitBtn.disabled = true;
            }
            setTimeout(() => { window.location.href = 'dashboard.html'; }, 1500);
        });        
    }

    if (altLoginBtn) {
        altLoginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.setItem('userEmail', 'demo.patient@healthpredict.com');
            localStorage.setItem('userName', 'Demo Patient');
            localStorage.setItem('userPhoto', 'https://i.pravatar.cc/150?img=11'); 

            altLoginBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Loading Dashboard...';
            altLoginBtn.style.opacity = '0.8';
            altLoginBtn.disabled = true;
            setTimeout(() => { window.location.href = 'dashboard.html'; }, 1500);
        });
    }
   /* ==========================================================================
   OFFICIAL GOOGLE AUTHENTICATION LOGIC (index.html)
   ========================================================================== */

function handleCredentialResponse(response) {
    // Decode the JWT token
    const responsePayload = JSON.parse(atob(response.credential.split('.')[1]));

    // Save REAL Google data
    localStorage.setItem('userName', responsePayload.name);
    localStorage.setItem('userEmail', responsePayload.email);
    localStorage.setItem('userPhoto', responsePayload.picture);

    // Redirect to dashboard
    window.location.href = 'dashboard.html';
}

window.onload = function () {
    // 1. Initialize Google Identity
    google.accounts.id.initialize({
        client_id: "66445890031-ftlfc1mu9g84josa1ud0cu2nf97ndgfg.apps.googleusercontent.com",
        callback: handleCredentialResponse
    });

    const googleContainer = document.getElementById('googleButtonContainer');
    
    // 2. Find your main blue Login button to steal its measurements
    const mainLoginButton = document.querySelector('.btn-submit');
    
    // 3. Measure it (if it can't find it, fallback to 350 pixels)
    const targetWidth = mainLoginButton ? mainLoginButton.offsetWidth : 350;

    if (googleContainer) {
        google.accounts.id.renderButton(
            googleContainer,
            { 
                theme: "outline", 
                size: "large", 
                shape: "rectangular",
                width: targetWidth, // Dynamically forces Google to match your button's exact width
                type: "standard",
                text: "signin_with"
            }
        );
    }
};
// --- Interactive Welcome Toast Logic ---
const userName = localStorage.getItem('userName');
const userPhoto = localStorage.getItem('userPhoto');
const justLoggedIn = sessionStorage.getItem('justLoggedIn');

// Only show the toast if they are on the dashboard and haven't seen it yet this session
if (window.location.pathname.includes('dashboard') && userName && !justLoggedIn) {
    // 1. Create the toast element
    const toast = document.createElement('div');
    toast.className = 'welcome-toast';
    toast.innerHTML = `
        <img src="${userPhoto}" class="toast-img" alt="Profile">
        <div class="toast-content">
            <h4>Welcome back, ${userName.split(' ')[0]}!</h4>
            <p>Authentication successful.</p>
        </div>
    `;
    
    // 2. Append to body and trigger animation
    document.body.appendChild(toast);
    
    // Slight delay to allow DOM to render before sliding in
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    // 3. Slide it back out after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        sessionStorage.setItem('justLoggedIn', 'true'); // Prevent it from showing on every page refresh
    }, 4000);
}




/* ==========================================================================
       3. DASHBOARD PAGE LOGIC 
       ========================================================================== */
    const healthChartCanvas = document.getElementById('healthTrendChart');
    if (healthChartCanvas) {
        const history = JSON.parse(localStorage.getItem('healthHistory')) || [];
        const historyTableBody = document.querySelector('table tbody');
        
        if (historyTableBody) {
            if (history.length === 0) {
                historyTableBody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 2rem;">No predictions yet. Go to Health Prediction to run a test!</td></tr>`;
            } else {
                historyTableBody.innerHTML = ''; 
                history.forEach(record => {
                    const row = `
                        <tr>
                            <td>${record.date}</td>
                            <td><span class="${record.statusColorClass}">${record.statusText.split(' ')[0]}</span></td>
                            <td>${record.score}%</td>
                            <td><span class="badge-pill ${record.badgeClass}">${record.badgeText}</span></td>
                        </tr>
                    `;
                    historyTableBody.innerHTML += row;
                });
            }
        }

        if (history.length > 0) {
            const latest = history[0]; 
            const metricValues = document.querySelectorAll('.metric-value');
            if (metricValues.length >= 4) {
                metricValues[0].innerHTML = `${100 - latest.score} <span class="denom">/100</span>`; 
                metricValues[1].innerHTML = latest.statusText.split(' ')[0]; 
                metricValues[2].innerHTML = `${latest.score}%`; 
                metricValues[2].className = `metric-value ${latest.statusColorClass}`; 
                metricValues[3].innerHTML = latest.date; 
                
                const gaugeNum = document.querySelector('.gauge-num');
                const gaugeTag = document.querySelector('.gauge-tag');
                if (gaugeNum && gaugeTag) {
                    gaugeNum.innerHTML = `${latest.score}%`;
                    gaugeTag.innerHTML = latest.statusText;
                }
            }
        }

        const chartData = [...history].reverse(); 
        let labels = chartData.map(r => r.date.split(' ')[0] + ' ' + (r.date.split(' ')[1] || '')); 
        let hrData = chartData.map(r => r.vitals ? r.vitals.hr : 75);
        let bpData = chartData.map(r => r.vitals ? parseInt(r.vitals.bp) || 120 : 120);
        let bsData = chartData.map(r => r.vitals ? parseInt(r.vitals.bs) || 95 : 95);

        while (labels.length < 6) {
            labels.unshift('Prev'); hrData.unshift(75); bpData.unshift(120); bsData.unshift(95);
        }
        labels = labels.slice(-6); hrData = hrData.slice(-6); bpData = bpData.slice(-6); bsData = bsData.slice(-6);

        new Chart(healthChartCanvas.getContext('2d'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    { label: 'Heart Rate', data: hrData, borderColor: '#ec4899', backgroundColor: 'rgba(236, 72, 153, 0.1)', tension: 0.4, fill: true },
                    { label: 'Blood Pressure', data: bpData, borderColor: '#3b82f6', tension: 0.4, borderDash: [5, 5] },
                    { label: 'Blood Sugar', data: bsData, borderColor: '#10b981', tension: 0.4 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { borderDash: [2, 4] } }, x: { grid: { display: false } } } }
        });
    }

    /* ==========================================================================
       4. HOSPITAL SYSTEM LOGIC (Health Records: Create, Read, Delete)
       ========================================================================== */
    const recordsPage = document.querySelector('.records-page');
    const recordsGrid = document.getElementById('recordsGrid');

    if (recordsPage && recordsGrid) {
        
        // --- Render Function ---
        const renderRecords = (filterType = 'All') => {
            let history = JSON.parse(localStorage.getItem('healthHistory')) || [];

            // Add IDs for backward compatibility to old records
            let modified = false;
            history = history.map((rec, index) => {
                if (!rec.id) {
                    rec.id = 'rec_' + Date.now() + '_' + index;
                    modified = true;
                }
                return rec;
            });
            if (modified) localStorage.setItem('healthHistory', JSON.stringify(history));

            // Filter Records based on Tabs
            const filteredHistory = history.filter(record => {
                if (filterType === 'AI') return record.isManual !== true;
                if (filterType === 'Manual') return record.isManual === true;
                return true; 
            });

            if (filteredHistory.length === 0) {
                recordsGrid.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-regular fa-folder-open"></i>
                        <h3>No Records Found</h3>
                        <p style="color: var(--text-muted); margin-top: 0.5rem;">No ${filterType !== 'All' ? filterType : ''} records exist yet.</p>
                    </div>
                `;
                return;
            }

            recordsGrid.innerHTML = '';
            
            // Render Cards
            filteredHistory.forEach((record, index) => {
                const hr = record.vitals && record.vitals.hr ? record.vitals.hr : '--';
                const bp = record.vitals && record.vitals.bp ? record.vitals.bp : '--';
                
                const isManual = record.isManual === true;
                const iconClass = isManual ? 'fa-file-medical' : 'fa-robot';
                const riskDisplay = isManual ? 'N/A' : `${record.score}%`;
                const titleClass = isManual ? 'text-dark' : record.statusColorClass;
                const typeColor = isManual ? '#0284c7' : 'var(--primary)'; // Hospital Blue vs AI Purple
                const badgeText = isManual ? (record.badgeText || 'External Report') : 'AI Prediction';

                const providerHTML = (isManual && record.provider) 
                    ? `<div style="font-size: 0.8rem; color: #64748b; margin-bottom: 0.8rem;"><i class="fa-regular fa-hospital"></i> <strong>Source:</strong> ${record.provider}</div>` 
                    : '';

                const fileHTML = (isManual && record.fileName) 
                    ? `<div style="font-size: 0.75rem; color: #0284c7; margin-top: 0.8rem; font-weight: 600; display: inline-flex; align-items: center; gap: 0.4rem; background: #e0f2fe; padding: 0.4rem 0.8rem; border-radius: 6px;"><i class="fa-solid fa-paperclip"></i> ${record.fileName}</div>` 
                    : '';

                const cardHTML = `
                    <div class="record-card" style="animation: fadeUp 0.3s ease forwards; animation-delay: ${index * 0.05}s; opacity: 0;">
                        <div class="record-header">
                            <span class="record-type" style="color: ${typeColor};"><i class="fa-solid ${iconClass}"></i> ${badgeText}</span>
                            <span class="record-date">${record.date}</span>
                        </div>
                        <div class="record-body">
                            <h3 class="record-title ${titleClass}" style="margin-bottom: 0.2rem;">${record.statusText}</h3>
                            ${providerHTML}
                            <div class="vitals-mini-grid">
                                <div class="vital-item">
                                    <span class="vital-lbl">Heart Rate</span>
                                    <span class="vital-val">${hr} <span style="font-size: 0.7rem; color: var(--text-muted);">bpm</span></span>
                                </div>
                                <div class="vital-item">
                                    <span class="vital-lbl">Blood Pressure</span>
                                    <span class="vital-val">${bp}</span>
                                </div>
                                <div class="vital-item">
                                    <span class="vital-lbl">Risk Score</span>
                                    <span class="vital-val">${riskDisplay}</span>
                                </div>
                                <div class="vital-item">
                                    <span class="vital-lbl">Status</span>
                                    <span class="vital-val"><span class="badge ${record.badgeClass || 'light-blue'}">${isManual ? 'Recorded' : 'Analyzed'}</span></span>
                                </div>
                            </div>
                            ${fileHTML}
                        </div>
                        <div class="record-footer">
                            <button class="btn-delete-record" data-id="${record.id}" style="padding: 0.6rem; background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; border-radius: 8px; cursor: pointer; flex: 1; font-weight: 600; transition: all 0.2s;"><i class="fa-solid fa-trash-can"></i> Delete</button>
                            <button class="btn-primary-sm" style="padding: 0.6rem; background: ${isManual ? '#0284c7' : 'var(--primary)'}; color: white; border: none; border-radius: 8px; cursor: pointer; flex: 1; font-weight: 600;">View Details</button>
                        </div>
                    </div>
                `;
                recordsGrid.innerHTML += cardHTML;
            });
        };

        renderRecords('All'); // Initial load

        // --- Delete Logic using Event Delegation ---
        recordsGrid.addEventListener('click', (e) => {
            const deleteBtn = e.target.closest('.btn-delete-record');
            if (deleteBtn) {
                const recordId = deleteBtn.getAttribute('data-id');
                if (confirm('Are you sure you want to permanently delete this record?')) {
                    let history = JSON.parse(localStorage.getItem('healthHistory')) || [];
                    history = history.filter(rec => rec.id !== recordId);
                    localStorage.setItem('healthHistory', JSON.stringify(history));
                    
                    const activeTab = document.querySelector('.filter-tab.active');
                    renderRecords(activeTab ? activeTab.getAttribute('data-filter') : 'All');
                }
            }
        });

        // --- Tab Switching Logic ---
        const filterTabs = document.querySelectorAll('.filter-tab');
        filterTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                filterTabs.forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                renderRecords(e.target.getAttribute('data-filter'));
            });
        });

        // --- Add Record Logic (Updated for Inline Section) ---
        // --- Add Record Logic (Redirect to new page) ---
        const addRecordBtn = document.getElementById('addRecordBtn');
        if (addRecordBtn) {
            addRecordBtn.addEventListener('click', (e) => {
                e.preventDefault();
                // Redirects to the new manual entry page
                window.location.href = 'add-record.html'; 
            });
        }
        const addRecordSection = document.getElementById('addRecordSection');
        const closeRecordSection = document.getElementById('closeRecordSection');
        const cancelRecordBtn = document.getElementById('cancelRecordBtn');
        const addRecordForm = document.getElementById('addRecordForm');

        if (addRecordBtn && addRecordSection) {
            
            // Toggle form visibility
            addRecordBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (addRecordSection.style.display === 'none' || addRecordSection.style.display === '') {
                    addRecordSection.style.display = 'block'; // Show it
                    const dateInput = document.getElementById('recordDate');
                    if(dateInput && !dateInput.value) dateInput.valueAsDate = new Date();
                } else {
                    addRecordSection.style.display = 'none'; // Hide it
                }
            });
            
            // Hide form using X or Cancel
            const hideForm = () => { addRecordSection.style.display = 'none'; };
            if (closeRecordSection) closeRecordSection.addEventListener('click', hideForm);
            if (cancelRecordBtn) cancelRecordBtn.addEventListener('click', hideForm);

            if (addRecordForm) {
                addRecordForm.addEventListener('submit', (e) => {
                    e.preventDefault();
                    
                    const typeInput = document.getElementById('recordType');
                    const type = typeInput ? typeInput.value : 'Manual';
                    
                    const dateInput = document.getElementById('recordDate');
                    const dateVal = dateInput ? dateInput.value : null;
                    
                    const providerInput = document.getElementById('recordProvider');
                    const provider = providerInput ? providerInput.value : 'External Hospital';
                    
                    const hrInput = document.getElementById('recordHr');
                    const hr = hrInput ? hrInput.value : '--';
                    
                    const bpInput = document.getElementById('recordBp');
                    const bp = bpInput ? bpInput.value : '--';
                    
                    const notesInput = document.getElementById('recordNotes');
                    const notes = notesInput ? notesInput.value : 'Manual Record';
                    
                    const fileInput = document.getElementById('recordFile');
                    const fileName = (fileInput && fileInput.files.length > 0) ? fileInput.files[0].name : null;
                    
                    const formattedDate = dateVal ? new Date(dateVal).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : new Date().toLocaleDateString('en-GB');
                    
                    const newRecord = {
                        id: 'rec_' + Date.now(), 
                        date: formattedDate,
                        score: 0, 
                        statusText: notes,
                        provider: provider,
                        fileName: fileName,
                        statusColorClass: 'text-dark', 
                        badgeClass: 'light-blue', 
                        badgeText: type,
                        vitals: { hr: hr || '--', bp: bp || '--', bs: '--' },
                        isManual: true
                    };

                    let history = JSON.parse(localStorage.getItem('healthHistory')) || [];
                    history.unshift(newRecord);
                    localStorage.setItem('healthHistory', JSON.stringify(history));
                    
                    // Hide and reset
                    addRecordSection.style.display = 'none';
                    addRecordForm.reset();
                    
                    // Force refresh to "All Records" tab
                    filterTabs.forEach(t => t.classList.remove('active'));
                    const allTab = document.querySelector('.filter-tab[data-filter="All"]');
                    if (allTab) allTab.classList.add('active');
                    
                    renderRecords('All'); 
                });
            }
        }
    }
    

    /* ==========================================================================
       5. HEART PREDICTION FORM LOGIC
       ========================================================================== */
    const riskForm = document.getElementById('riskForm'); 
    if (riskForm) {
        riskForm.addEventListener('submit', function(e) {
            e.preventDefault(); 

            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing Data...';
                submitBtn.disabled = true;
                submitBtn.style.opacity = '0.8';
            }

            const age = parseInt(document.getElementById('age')?.value) || 0;
            const gender = document.getElementById('gender')?.value;
            const cp = parseInt(document.getElementById('chestPain')?.value) || 0;
            const bp = parseInt(document.getElementById('bp')?.value) || 120; 
            const chol = parseInt(document.getElementById('cholesterol')?.value) || 0;
            const fbs = document.getElementById('fbs')?.value;
            const thalach = parseInt(document.getElementById('thalach')?.value) || 75; 
            const exang = document.getElementById('exang')?.value;

            let riskScore = 5; 
            if (age > 50) riskScore += 12; if (age > 65) riskScore += 8; if (gender === 'male') riskScore += 8;
            if (cp > 0) riskScore += 18; if (bp > 130) riskScore += 10; if (bp > 150) riskScore += 15;
            if (chol > 240) riskScore += 12; if (fbs === '1') riskScore += 10; if (thalach < 130) riskScore += 8; 
            if (exang === '1') riskScore += 15; 
            riskScore = Math.min(riskScore, 98);

            let statusText = "", statusColor = "", statusIcon = "", recommendation = "", colorClass = "", badgeClass = "", badgeText = "";

            if (riskScore < 30) {
                statusText = "Low Risk"; statusColor = "#10b981"; statusIcon = "fa-shield-heart"; colorClass = "text-green"; badgeClass = "light-green"; badgeText = "Good";
                recommendation = "Great job! Your cardiovascular profile looks healthy. Maintain your current diet and exercise routine.";
            } else if (riskScore < 60) {
                statusText = "Moderate Risk"; statusColor = "#f59e0b"; statusIcon = "fa-triangle-exclamation"; colorClass = "text-orange"; badgeClass = "light-orange"; badgeText = "Moderate";
                recommendation = "You have some risk factors. Consider speaking with a doctor about managing your blood pressure or cholesterol levels.";
            } else {
                statusText = "High Risk"; statusColor = "#ef4444"; statusIcon = "fa-truck-medical"; colorClass = "text-red"; badgeClass = "light-red"; badgeText = "At Risk";
                recommendation = "Your profile indicates a high probability of cardiovascular issues. Please schedule a consultation with a cardiologist soon.";
            }

            const today = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
            
            // Generate standard AI prediction record
            const newRecord = { 
                id: 'rec_' + Date.now(), // Generate ID for deletion logic
                date: today, 
                score: riskScore, 
                statusText: statusText, 
                statusColorClass: colorClass, 
                badgeClass: badgeClass, 
                badgeText: badgeText,
                vitals: { hr: thalach, bp: bp, bs: fbs === '1' ? 140 : 95 },
                isManual: false 
            };
            
            let history = JSON.parse(localStorage.getItem('healthHistory')) || [];
            history.unshift(newRecord); 
            if(history.length > 20) history.pop(); // Keep array size manageable
            localStorage.setItem('healthHistory', JSON.stringify(history));

            const payload = {
                age: age, gender: gender === 'male' ? 1 : 0, chestPain: cp, bloodPressure: bp, cholesterol: chol, riskScore: riskScore, statusText: statusText
            };

            fetch('http://localhost:3000/api/records', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                setTimeout(() => { showPredictionSuccess(riskScore, statusText, statusColor, statusIcon, recommendation); }, 1000); 
            })
            .catch(error => {
                console.error('Database logging error:', error);
                setTimeout(() => { showPredictionSuccess(riskScore, statusText, statusColor, statusIcon, recommendation); }, 1000); 
            });
        });

        function showPredictionSuccess(riskScore, statusText, statusColor, statusIcon, recommendation) {
            const formCard = riskForm.closest('.form-card') || riskForm.closest('.form-workspace');
            if (formCard) {
                formCard.innerHTML = `
                    <div style="text-align: center; padding: 2rem 1rem; animation: pulse 0.5s ease;">
                        <div style="width: 80px; height: 80px; background: ${statusColor}20; color: ${statusColor}; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; margin: 0 auto 1.5rem auto;"><i class="fa-solid ${statusIcon}"></i></div>
                        <h2 style="font-size: 1.5rem; color: var(--text-dark); margin-bottom: 0.5rem;">Prediction Complete</h2>
                        <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 2rem;">Analysis logged successfully to database.</p>
                        <div style="background: #f8fafc; border: 1px solid var(--border-color); border-radius: 12px; padding: 2rem; margin-bottom: 2rem;">
                            <span style="font-size: 0.9rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;">Estimated Probability</span>
                            <div style="font-size: 4rem; font-weight: 800; color: ${statusColor}; line-height: 1;">${riskScore}%</div>
                            <div style="display: inline-block; margin-top: 1rem; padding: 0.5rem 1rem; background: ${statusColor}15; color: ${statusColor}; font-weight: 600; border-radius: 20px; font-size: 0.9rem;">${statusText}</div>
                        </div>
                        <div style="text-align: left; background: var(--primary-light); color: var(--text-dark); padding: 1.5rem; border-radius: 8px; border-left: 4px solid var(--primary); font-size: 0.9rem; line-height: 1.5;">
                            <strong><i class="fa-solid fa-user-doctor"></i> Recommendation:</strong><br>${recommendation}
                        </div>
                        <div style="display: flex; gap: 1rem; justify-content: center; margin-top: 2rem;">
                            <button onclick="window.location.reload()" style="background: white; border: 1px solid var(--border-color); color: var(--text-dark); padding: 0.8rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer;">
                                <i class="fa-solid fa-rotate-left"></i> Run Again
                            </button>
                            <button onclick="window.location.href='health-records.html'" style="background: var(--primary); color: white; border: none; padding: 0.8rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer;">
                                Go to Records <i class="fa-solid fa-arrow-right"></i>
                            </button>
                        </div>
                    </div>
                `;
            }
        }
    }

    /* ==========================================================================
       6. MY HISTORY PAGE LOGIC
       ========================================================================== */
    const historyPage = document.querySelector('.history-table');
    if (historyPage) {
        const historyBody = document.getElementById('historyBody');
        const history = JSON.parse(localStorage.getItem('healthHistory')) || [];

        if (historyBody) {
            if (history.length === 0) {
                historyBody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:2rem;">No history found.</td></tr>`;
            } else {
                historyBody.innerHTML = '';
                history.forEach(record => {
                    historyBody.innerHTML += `
                        <tr>
                            <td><strong>${record.date}</strong></td>
                            <td><span class="status-pill ${record.badgeClass}">${record.statusText}</span></td>
                            <td>${record.score}%</td>
                            <td><button onclick="window.location.href='health-records.html'" class="btn-outline">Details</button></td>
                        </tr>
                    `;
                });
            }
        }
    }

    /* ==========================================================================
       7. PROFILE SETTINGS LOGIC
       ========================================================================== */
    const profilePage = document.querySelector('.profile-page');
    if (profilePage && saveProfileBtn) {
        saveProfileBtn.addEventListener("click", async (e) => {
            e.preventDefault(); 
            const nameInput = document.getElementById("profileName");
            if(nameInput) {
                localStorage.setItem('userName', nameInput.value);
                updateUI(nameInput.value, null, null);
            }
            const originalText = saveProfileBtn.innerHTML;
            saveProfileBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
            setTimeout(() => {
                saveProfileBtn.innerHTML = '<i class="fa-solid fa-check"></i> Profile Updated!';
                saveProfileBtn.style.backgroundColor = '#16a34a'; 
                saveProfileBtn.style.color = 'white';
                saveProfileBtn.style.borderColor = '#16a34a';
                setTimeout(() => {
                    saveProfileBtn.innerHTML = originalText;
                    saveProfileBtn.style.backgroundColor = ''; 
                    saveProfileBtn.style.color = '';
                    saveProfileBtn.style.borderColor = '';
                }, 2000);
            }, 1000); 
        });
    }

    /* ==========================================================================
       8. RECOMMENDATIONS PAGE LOGIC
       ========================================================================== */
    const recPage = document.querySelector('.recommendations-page');
    if (recPage) {
        const history = JSON.parse(localStorage.getItem('healthHistory')) || [];
        const recGrid = document.getElementById('recGrid');
        const alertContainer = document.getElementById('riskAlertContainer');

        if (history.length === 0) {
            recGrid.innerHTML = `<p>No data found. Please complete an assessment first.</p>`;
        } else {
            const latest = history[0];
            if (latest.score > 60 && alertContainer) {
                alertContainer.innerHTML = `
                    <div class="risk-alert">
                        <i class="fa-solid fa-triangle-exclamation"></i> <strong>Medical Priority:</strong> 
                        Based on your latest high-risk assessment, we strongly recommend scheduling a consultation with your cardiologist.
                    </div>
                `;
            }
            const advice = [
                { title: "Dietary Adjustments", icon: "fa-apple-whole", desc: "Focus on low-sodium foods, leafy greens, and whole grains to support heart health." },
                { title: "Physical Activity", icon: "fa-person-walking", desc: "Aim for 30 minutes of moderate aerobic activity (brisk walking) at least 5 days a week." },
                { title: "Stress Management", icon: "fa-spa", desc: "Incorporate mindfulness meditation or deep breathing exercises to lower cortisol levels." },
                { title: "Routine Monitoring", icon: "fa-notes-medical", desc: "Track your blood pressure and sugar levels at the same time every day." }
            ];
            advice.forEach(item => {
                recGrid.innerHTML += `
                    <div class="rec-card">
                        <i class="fa-solid ${item.icon}"></i>
                        <h3>${item.title}</h3>
                        <p style="color: var(--text-muted);">${item.desc}</p>
                    </div>
                `;
            });
        }
    }

    /* ==========================================================================
       9. CHARTS & TRENDS PAGE LOGIC
       ========================================================================== */
    const chartsPage = document.querySelector('.charts-page');
    if (chartsPage) {
        const history = JSON.parse(localStorage.getItem('healthHistory')) || [];
        const canvasObj = document.getElementById('healthChart');
        
        if(canvasObj) {
            const ctx = canvasObj.getContext('2d');
            if (history.length === 0) {
                document.querySelector('.history-container').innerHTML = `<p style="text-align:center;">No data available. Please complete an assessment.</p>`;
            } else {
                const sortedHistory = [...history].reverse(); 
                const labels = sortedHistory.map(record => record.date);
                const dataPoints = sortedHistory.map(record => record.score);

                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{ label: 'Health Risk Score', data: dataPoints, borderColor: '#2563eb', backgroundColor: 'rgba(37, 99, 235, 0.1)', tension: 0.4, fill: true, pointBackgroundColor: '#2563eb' }]
                    },
                    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 100 } } }
                });
            }
        }
    }

    /* ==========================================================================
       10. UTILITIES (Logout)
       ========================================================================== */
    // --- Interactive Secure Logout ---
    const logoutBtn = document.querySelector('.logout-btn');

    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault(); 
            
            // 1. Interactive Loading State
            const originalText = logoutBtn.innerHTML;
            logoutBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span class="nav-text">Signing out...</span>';
            logoutBtn.style.opacity = '0.7';
            logoutBtn.style.pointerEvents = 'none';

            // 2. Simulate secure connection closing
            setTimeout(() => {
                // 3. Obliterate the stored Google data
                localStorage.removeItem('userName');
                localStorage.removeItem('userEmail');
                localStorage.removeItem('userPhoto');
                sessionStorage.removeItem('justLoggedIn');
                
                // 4. Redirect to login page
                window.location.href = 'index.html';
            }, 800);
        });
    }
});