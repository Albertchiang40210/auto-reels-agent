// --- 登入系統 ---
function login() {
    const pwd = document.getElementById('passwordInput').value;
    const errorMsg = document.getElementById('loginError');
    if (pwd === 'admin123') {
        document.getElementById('loginScreen').classList.add('hidden');
        document.getElementById('mainDashboard').classList.remove('hidden');
        // 登入成功後載入左側影片清單與右側監控面板
        loadVideos();
        loadIGFeed();
    } else {
        errorMsg.classList.remove('hidden');
    }
}

// 支援 Enter 登入
document.getElementById('passwordInput').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') login();
});

// --- 左側發文儀表板邏輯 ---
async function loadVideos() {
    const select = document.getElementById('videoSelect');
    select.innerHTML = '<option value="">載入中...</option>';
    
    try {
        const res = await fetch('/api/videos');
        const data = await res.json();
        
        if (data.videos.length === 0) {
            select.innerHTML = '<option value="">(草稿區沒有影片，請先把影片放入 draft_videos/)</option>';
            document.getElementById('topicInput').value = '';
        } else {
            select.innerHTML = data.videos.map(v => `<option value="${v}">${v}</option>`).join('');
            const firstVideo = data.videos[0];
            const topic = firstVideo.replace(/\.[^/.]+$/, "");
            document.getElementById('topicInput').value = topic;
        }
    } catch (err) {
        select.innerHTML = '<option value="">載入影片失敗</option>';
    }
}

document.getElementById('videoSelect').addEventListener('change', function(e) {
    if (e.target.value) {
        const topic = e.target.value.replace(/\.[^/.]+$/, "");
        document.getElementById('topicInput').value = topic;
    }
});

async function generateCaption() {
    const topic = document.getElementById('topicInput').value.trim();
    if (!topic) { alert('請確認影片主題！'); return; }
    
    const btn = document.getElementById('generateBtn');
    const loading = document.getElementById('loading');
    const loadingText = document.getElementById('loadingText');
    const result = document.getElementById('result');
    const successScreen = document.getElementById('successScreen');
    
    btn.disabled = true;
    result.classList.add('hidden');
    successScreen.classList.add('hidden');
    loading.classList.remove('hidden');
    loadingText.innerText = "背景任務已啟動，正在上網搜尋資料與分析影片...";
    
    try {
        const response = await fetch('/api/generate_caption', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                topic: topic,
                filename: document.getElementById('videoSelect').value
            })
        });
        const taskData = await response.json();
        if (!response.ok) throw new Error(taskData.detail);
        
        const taskId = taskData.task_id;
        
        // 開始輪詢檢查任務狀態
        const checkStatus = setInterval(async () => {
            const statusRes = await fetch(`/api/task_status/${taskId}`);
            const statusData = await statusRes.json();
            
            if (statusData.status === "processing") {
                // 更新 loading 文字，增加動態感
                const dots = loadingText.innerText.split('.').length - 1;
                loadingText.innerText = `雙 Agent 激烈討論中${'.'.repeat((dots % 3) + 1)}`;
            } else if (statusData.status === "completed") {
                clearInterval(checkStatus);
                const data = statusData.data;
                
                // 處理優化建議
                const suggestionsBox = document.getElementById('suggestionsBox');
                if (data.suggestions) {
                    document.getElementById('suggestionsText').innerText = data.suggestions;
                    suggestionsBox.classList.remove('hidden');
                } else {
                    suggestionsBox.classList.add('hidden');
                }
                
                // 處理 A/B 測試卡片
                const optionsContainer = document.getElementById('optionsContainer');
                optionsContainer.innerHTML = '';
                
                if (data.options && data.options.length > 0) {
                    data.options.forEach((opt, index) => {
                        const card = document.createElement('div');
                        card.style.cssText = `
                            flex: 1; min-width: 120px; padding: 10px; border: 2px solid #e2e8f0; 
                            border-radius: 8px; cursor: pointer; text-align: center;
                            background: white; transition: all 0.2s;
                        `;
                        card.innerHTML = `<h5 style="margin:0; color:#334155; font-size:1rem;">${opt.style}</h5>`;
                        card.onclick = () => {
                            // 移除所有 active 狀態
                            Array.from(optionsContainer.children).forEach(c => {
                                c.style.borderColor = '#e2e8f0';
                                c.style.background = 'white';
                            });
                            // 設定當前為 active
                            card.style.borderColor = '#3b82f6';
                            card.style.background = '#eff6ff';
                            
                            // 填入 Editor
                            document.getElementById('captionEditor').value = opt.caption || "";
                            document.getElementById('voiceEditor').value = opt.voice_script || "";
                        };
                        optionsContainer.appendChild(card);
                    });
                    // 預設點擊第一個選項
                    optionsContainer.children[0].click();
                } else {
                    // 相容舊格式或降級模式
                    document.getElementById('captionEditor').value = data.caption || "";
                    document.getElementById('voiceEditor').value = data.voice_script || "";
                }
                
                loading.classList.add('hidden');
                result.classList.remove('hidden');
                btn.disabled = false;
            }
        }, 2000); // 每 2 秒輪詢一次
        
    } catch (error) {
        alert('生成失敗：' + error.message);
        loading.classList.add('hidden');
        btn.disabled = false;
    }
}

async function publishToIG() {
    const filename = document.getElementById('videoSelect').value;
    const caption = document.getElementById('captionEditor').value;
    const voiceScript = document.getElementById('voiceEditor').value;
    const useAiVoice = document.getElementById('useAiVoice').checked;
    
    if (!filename) { alert('請先選擇影片！'); return; }
    
    const btn = document.getElementById('publishBtn');
    btn.disabled = true;
    
    if (useAiVoice) {
        btn.innerText = '🔊 正在合成語音與轉檔，這可能需要幾十秒鐘...';
    } else {
        btn.innerText = '🔄 正在轉檔與發布中...';
    }
    
    try {
        const response = await fetch('/api/publish', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                filename: filename, 
                caption: caption,
                use_ai_voice: useAiVoice,
                voice_script: voiceScript
            })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail);
        
        document.getElementById('result').classList.add('hidden');
        document.getElementById('successScreen').classList.remove('hidden');
        
        // 發布成功後，立刻重新載入右側監控面板！
        loadIGFeed();
        
    } catch (error) {
        alert('發布失敗：' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerText = '🚀 確定沒問題，正式發布';
    }
}

function resetDashboard() {
    document.getElementById('successScreen').classList.add('hidden');
    loadVideos();
}

// --- 右側切換分頁邏輯 ---
function switchTab(tabId) {
    document.getElementById('tabFeedBtn').classList.remove('active');
    document.getElementById('tabAnalyticsBtn').classList.remove('active');
    document.getElementById('igFeed').classList.add('hidden');
    document.getElementById('analyticsPanel').classList.add('hidden');
    
    if (tabId === 'feed') {
        document.getElementById('tabFeedBtn').classList.add('active');
        document.getElementById('igFeed').classList.remove('hidden');
        loadIGFeed();
    } else {
        document.getElementById('tabAnalyticsBtn').classList.add('active');
        document.getElementById('analyticsPanel').classList.remove('hidden');
        loadAnalytics();
    }
}

// --- 右側 IG 監控面板邏輯 ---
const mockComments = [
    "太狂了吧！這個消息真的準確嗎？🔥",
    "這台車我等好久了，謝謝大大分享！",
    "立刻標記我朋友來看 @john_doe",
    "想知道什麼時候台灣會上市？",
    "影片剪得很棒耶！追蹤了～"
];

async function loadIGFeed() {
    const feedContainer = document.getElementById('igFeed');
    feedContainer.innerHTML = '<p style="text-align:center; color:#94a3b8; margin-top:50px;">同步資料中...</p>';
    
    try {
        const [resVideos, resAnalytics] = await Promise.all([
            fetch('/api/published_videos'),
            fetch('/api/analytics')
        ]);
        const data = await resVideos.json();
        const analyticsData = await resAnalytics.json();
        
        if (data.videos.length === 0) {
            feedContainer.innerHTML = `
                <div style="text-align:center; color:#64748b; margin-top:50px;">
                    <p style="font-size:3rem; margin-bottom:10px;">📭</p>
                    <p>尚未發布任何貼文</p>
                    <p style="font-size:0.9rem;">當你從左側成功發布影片後，這裡會出現即時貼文動態。</p>
                </div>
            `;
            return;
        }
        
        const reversedVideos = data.videos.reverse();
        let html = '';
        reversedVideos.forEach((video, index) => {
            const randomLikes = Math.floor(Math.random() * 5000) + 100;
            const topic = video.replace('ig_ready_', '').replace(/\.[^/.]+$/, "");
            const actualCaption = analyticsData[topic]?.caption || `關於【${topic}】的最新貼文已成功上傳至 Instagram！`;
            const displayCaption = actualCaption.replace(/\n/g, '<br>');
            
            const c1 = mockComments[Math.floor(Math.random() * mockComments.length)];
            const c2 = mockComments[Math.floor(Math.random() * mockComments.length)];
            
            html += `
                <div class="ig-post">
                    <div class="ig-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div class="ig-avatar">Auto</div>
                            <div class="ig-username" style="margin: 0;">Auto Reels 官方小編 <span style="color:#3b82f6; font-size:0.8rem;">✓</span></div>
                        </div>
                        <div style="display: flex; gap: 5px;">
                            <button onclick="editPost('${topic}')" style="background: none; border: none; color: #3b82f6; font-size: 0.9rem; cursor: pointer; padding: 5px; opacity: 0.7; transition: opacity 0.2s;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.7" title="編輯此貼文文案">✏️ 編輯</button>
                            <button onclick="deletePost('${video}')" style="background: none; border: none; color: #ef4444; font-size: 0.9rem; cursor: pointer; padding: 5px; opacity: 0.7; transition: opacity 0.2s;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.7" title="刪除此貼文">🗑️ 刪除</button>
                        </div>
                    </div>
                    <div class="ig-media" style="width: 100%; background: black; display: flex; align-items: center; justify-content: center; overflow: hidden; border-radius: 4px; aspect-ratio: 4/5;">
                        <video src="/published_videos/${encodeURIComponent(video)}" controls style="width: 100%; height: 100%; object-fit: contain;"></video>
                    </div>
                    <div class="ig-actions"><span>❤️</span> <span>💬</span> <span>✈️</span> <span>🔖</span></div>
                    <div class="ig-likes">${randomLikes.toLocaleString()} 個讚</div>
                    <div class="ig-caption" style="font-size: 0.95rem; margin-top:5px; color:#334155;">
                        <span style="font-weight:700; color:#1e293b;">Auto Reels 官方小編</span> ${displayCaption}
                    </div>
                    <div class="ig-comments-section">
                        <div class="ig-comment"><span style="font-weight:700; color:#1e293b;">user_abc88</span> ${c1}</div>
                        <div class="ig-comment"><span style="font-weight:700; color:#1e293b;">car_lover_99</span> ${c2}</div>
                    </div>
                </div>
            `;
        });
        feedContainer.innerHTML = html;
        
        // 如果目前正在搜尋，重新觸發搜尋邏輯以確保畫面正確
        const searchInput = document.getElementById('feedSearchInput');
        if (searchInput && searchInput.value) {
            searchInput.dispatchEvent(new Event('input'));
        }
    } catch (err) {
        feedContainer.innerHTML = '<p style="text-align:center; color:#ef4444; margin-top:50px;">載入狀態失敗</p>';
    }
}

// --- 編輯貼文邏輯 ---
async function editPost(topic) {
    const newCaption = prompt('✏️ 請輸入新的貼文文案：');
    if (newCaption === null) return; // 使用者按取消
    
    try {
        const response = await fetch(`/api/published_videos/${topic}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ caption: newCaption })
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || '更新失敗');
        }
        
        // 重新載入動態牆
        loadIGFeed();
    } catch (err) {
        alert('更新失敗：' + err.message);
    }
}

// --- 刪除貼文邏輯 ---
async function deletePost(filename) {
    if (!confirm('⚠️ 確定要刪除這則貼文嗎？\\n這將會刪除實體影片檔案與相關的成效數據，且無法復原！')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/published_videos/${filename}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || '刪除失敗');
        }
        
        // 重新載入動態牆與分析圖表
        loadIGFeed();
        if (document.getElementById('analyticsPanel') && !document.getElementById('analyticsPanel').classList.contains('hidden')) {
            loadAnalytics();
        }
        
    } catch (err) {
        alert('刪除失敗：' + err.message);
    }
}

// --- 貼文搜尋過濾邏輯 ---
document.getElementById('feedSearchInput')?.addEventListener('input', function(e) {
    const keyword = e.target.value.toLowerCase().trim();
    const posts = document.querySelectorAll('#igFeed .ig-post');
    
    let visibleCount = 0;
    posts.forEach(post => {
        const textContent = post.innerText.toLowerCase();
        if (textContent.includes(keyword)) {
            post.style.display = 'block';
            visibleCount++;
        } else {
            post.style.display = 'none';
        }
    });
    
    // 如果搜尋結果為空，顯示提示
    const feedContainer = document.getElementById('igFeed');
    let noResultMsg = document.getElementById('noSearchResult');
    
    if (visibleCount === 0 && posts.length > 0) {
        if (!noResultMsg) {
            noResultMsg = document.createElement('div');
            noResultMsg.id = 'noSearchResult';
            noResultMsg.style.cssText = 'text-align:center; color:#94a3b8; margin-top:30px; font-size: 0.95rem;';
            noResultMsg.innerHTML = '🔍 找不到相關的貼文...';
            feedContainer.appendChild(noResultMsg);
        }
        noResultMsg.style.display = 'block';
    } else if (noResultMsg) {
        noResultMsg.style.display = 'none';
    }
});

// --- Chart.js 分析圖表邏輯 ---
let engagementChartInstance = null;
let ctrChartInstance = null;
let sentimentChartInstance = null;

async function loadAnalytics() {
    try {
        const res = await fetch('/api/analytics');
        const data = await res.json();
        
        const allTopics = Object.keys(data);
        
        // --- KPI 數據計算 (基於所有貼文) ---
        let totalEngagement = 0;
        let totalCtr = 0;
        let maxEngagement = 0;
        let topPost = "-";
        
        let avgPos = 0, avgNeu = 0, avgNeg = 0;
        
        if (allTopics.length > 0) {
            allTopics.forEach(t => {
                const engagement = data[t].likes + data[t].comments;
                totalEngagement += engagement;
                totalCtr += data[t].ctr;
                
                if (engagement > maxEngagement) {
                    maxEngagement = engagement;
                    topPost = t;
                }
                
                const s = data[t].sentiment || { positive: 60, neutral: 30, negative: 10 };
                avgPos += s.positive;
                avgNeu += s.neutral;
                avgNeg += s.negative;
            });
            
            avgPos = Math.round(avgPos / allTopics.length);
            avgNeu = Math.round(avgNeu / allTopics.length);
            avgNeg = Math.round(avgNeg / allTopics.length);
            
            document.getElementById('kpiTotalEngagement').innerText = totalEngagement.toLocaleString();
            document.getElementById('kpiAvgCtr').innerText = (totalCtr / allTopics.length).toFixed(1) + "%";
            document.getElementById('kpiTopPost').innerText = topPost;
        }
        
        // --- 圖表資料限制 (只取最後 10 筆) ---
        let chartTopics = [...allTopics];
        if (chartTopics.length > 10) {
            chartTopics = chartTopics.slice(-10);
        }
        
        const likes = chartTopics.map(t => data[t].likes);
        const comments = chartTopics.map(t => data[t].comments);
        const ctrs = chartTopics.map(t => data[t].ctr);
        
        if (chartTopics.length === 0) {
            chartTopics.push('暫無資料');
            likes.push(0); comments.push(0); ctrs.push(0);
        }
        
        // --- 視覺體驗升級：加入漸層色 ---
        const ctxEng = document.getElementById('engagementChart').getContext('2d');
        const gradLikes = ctxEng.createLinearGradient(0, 0, 0, 400);
        gradLikes.addColorStop(0, '#fbd38d');
        gradLikes.addColorStop(1, '#f6ad55');
        
        const gradComments = ctxEng.createLinearGradient(0, 0, 0, 400);
        gradComments.addColorStop(0, '#f687b3');
        gradComments.addColorStop(1, '#d53f8c');

        if (engagementChartInstance) engagementChartInstance.destroy();
        engagementChartInstance = new Chart(ctxEng, {
            type: 'bar',
            data: {
                labels: chartTopics,
                datasets: [
                    { label: '按讚數', data: likes, backgroundColor: gradLikes, borderRadius: 4 },
                    { label: '留言數', data: comments, backgroundColor: gradComments, borderRadius: 4 }
                ]
            },
            options: {
                responsive: true,
                interaction: { mode: 'index', intersect: false },
                scales: { 
                    y: { beginAtZero: true, grid: { color: '#f1f5f9' }, ticks: { color: '#64748b' } }, 
                    x: { grid: { display: false }, ticks: { color: '#64748b', maxRotation: 45, minRotation: 45 } } 
                },
                plugins: { 
                    legend: { labels: { color: '#1e293b', font: { weight: 'bold' } } },
                    tooltip: { backgroundColor: 'rgba(15, 23, 42, 0.9)', titleFont: { size: 14 }, bodyFont: { size: 13 }, padding: 10, cornerRadius: 8 }
                }
            }
        });
        
        const ctxCtr = document.getElementById('ctrChart').getContext('2d');
        const gradCtr = ctxCtr.createLinearGradient(0, 0, 0, 400);
        gradCtr.addColorStop(0, 'rgba(236, 72, 153, 0.4)');
        gradCtr.addColorStop(1, 'rgba(236, 72, 153, 0.0)');

        if (ctrChartInstance) ctrChartInstance.destroy();
        ctrChartInstance = new Chart(ctxCtr, {
            type: 'line',
            data: {
                labels: chartTopics,
                datasets: [{
                    label: '點擊率 (CTR %)', data: ctrs, borderColor: '#ec4899', borderWidth: 3,
                    backgroundColor: gradCtr, fill: true, tension: 0.4,
                    pointBackgroundColor: '#fff', pointBorderColor: '#ec4899', pointBorderWidth: 2, pointRadius: 4, pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                interaction: { mode: 'index', intersect: false },
                scales: { 
                    y: { beginAtZero: true, grid: { color: '#f1f5f9' }, ticks: { color: '#64748b' } }, 
                    x: { grid: { display: false }, ticks: { color: '#64748b', maxRotation: 45, minRotation: 45 } } 
                },
                plugins: { 
                    legend: { labels: { color: '#1e293b', font: { weight: 'bold' } } },
                    tooltip: { backgroundColor: 'rgba(15, 23, 42, 0.9)', titleFont: { size: 14 }, bodyFont: { size: 13 }, padding: 10, cornerRadius: 8 }
                }
            }
        });

        const ctxSent = document.getElementById('sentimentChart').getContext('2d');
        if (sentimentChartInstance) sentimentChartInstance.destroy();
        sentimentChartInstance = new Chart(ctxSent, {
            type: 'doughnut',
            data: {
                labels: ['好評 (Positive)', '中立 (Neutral)', '負評 (Negative)'],
                datasets: [{
                    data: [avgPos, avgNeu, avgNeg],
                    backgroundColor: ['#10b981', '#94a3b8', '#f43f5e'],
                    hoverOffset: 4,
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                cutout: '65%',
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#1e293b', font: { weight: 'bold' }, padding: 15 } },
                    tooltip: { backgroundColor: 'rgba(15, 23, 42, 0.9)', padding: 10, cornerRadius: 8 }
                }
            }
        });

    } catch (err) {
        console.error('載入分析數據失敗', err);
    }
}
