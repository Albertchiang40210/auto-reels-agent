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
    const result = document.getElementById('result');
    const successScreen = document.getElementById('successScreen');
    
    btn.disabled = true;
    result.classList.add('hidden');
    successScreen.classList.add('hidden');
    loading.classList.remove('hidden');
    
    try {
        const response = await fetch('/api/generate_caption', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: topic })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail);
        
        document.getElementById('captionEditor').value = data.caption || "";
        document.getElementById('voiceEditor').value = data.voice_script || "";
        loading.classList.add('hidden');
        result.classList.remove('hidden');
    } catch (error) {
        alert('生成失敗：' + error.message);
        loading.classList.add('hidden');
    } finally {
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
        const res = await fetch('/api/published_videos');
        const data = await res.json();
        
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
            const c1 = mockComments[Math.floor(Math.random() * mockComments.length)];
            const c2 = mockComments[Math.floor(Math.random() * mockComments.length)];
            
            html += `
                <div class="ig-post">
                    <div class="ig-header">
                        <div class="ig-avatar">Auto</div>
                        <div class="ig-username">Auto Reels 官方小編 <span style="color:#3b82f6; font-size:0.8rem;">✓</span></div>
                    </div>
                    <div class="ig-media">▶️ 已發布影片：<br>${video}</div>
                    <div class="ig-actions"><span>❤️</span> <span>💬</span> <span>✈️</span> <span>🔖</span></div>
                    <div class="ig-likes">${randomLikes.toLocaleString()} 個讚</div>
                    <div class="ig-caption" style="font-size: 0.95rem; margin-top:5px; color:#334155;">
                        <span style="font-weight:700; color:#1e293b;">Auto Reels 官方小編</span> 關於【${topic}】的最新貼文已成功上傳至 Instagram！
                    </div>
                    <div class="ig-comments-section">
                        <div class="ig-comment"><span style="font-weight:700; color:#1e293b;">user_abc88</span> ${c1}</div>
                        <div class="ig-comment"><span style="font-weight:700; color:#1e293b;">car_lover_99</span> ${c2}</div>
                    </div>
                </div>
            `;
        });
        feedContainer.innerHTML = html;
    } catch (err) {
        feedContainer.innerHTML = '<p style="text-align:center; color:#ef4444; margin-top:50px;">載入狀態失敗</p>';
    }
}

// --- Chart.js 分析圖表邏輯 ---
let engagementChartInstance = null;
let ctrChartInstance = null;
let sentimentChartInstance = null;

async function loadAnalytics() {
    try {
        const res = await fetch('/api/analytics');
        const data = await res.json();
        
        const topics = Object.keys(data);
        const likes = topics.map(t => data[t].likes);
        const comments = topics.map(t => data[t].comments);
        const ctrs = topics.map(t => data[t].ctr);
        
        let avgPos = 0, avgNeu = 0, avgNeg = 0;
        if (topics.length === 0) {
            topics.push('暫無資料');
            likes.push(0); comments.push(0); ctrs.push(0);
        } else {
            // 計算總平均輿情
            topics.forEach(t => {
                const s = data[t].sentiment || { positive: 60, neutral: 30, negative: 10 };
                avgPos += s.positive;
                avgNeu += s.neutral;
                avgNeg += s.negative;
            });
            avgPos = Math.round(avgPos / topics.length);
            avgNeu = Math.round(avgNeu / topics.length);
            avgNeg = Math.round(avgNeg / topics.length);
        }
        
        // 渲染互動數圖表
        const ctxEng = document.getElementById('engagementChart').getContext('2d');
        if (engagementChartInstance) engagementChartInstance.destroy();
        engagementChartInstance = new Chart(ctxEng, {
            type: 'bar',
            data: {
                labels: topics,
                datasets: [
                    { label: '按讚數', data: likes, backgroundColor: '#f09433' },
                    { label: '留言數', data: comments, backgroundColor: '#cc2366' }
                ]
            },
            options: {
                responsive: true,
                scales: { 
                    y: { beginAtZero: true, grid: { color: '#e2e8f0' }, ticks: { color: '#64748b' } }, 
                    x: { grid: { display: false }, ticks: { color: '#64748b' } } 
                },
                plugins: { legend: { labels: { color: '#1e293b', font: { weight: 'bold' } } } }
            }
        });
        
        // 渲染點擊率圖表
        const ctxCtr = document.getElementById('ctrChart').getContext('2d');
        if (ctrChartInstance) ctrChartInstance.destroy();
        ctrChartInstance = new Chart(ctxCtr, {
            type: 'line',
            data: {
                labels: topics,
                datasets: [{
                    label: '點擊率 (CTR %)', data: ctrs, borderColor: '#ec4899',
                    backgroundColor: 'rgba(236, 72, 153, 0.1)', fill: true, tension: 0.4,
                    pointBackgroundColor: '#ec4899'
                }]
            },
            options: {
                responsive: true,
                scales: { 
                    y: { beginAtZero: true, grid: { color: '#e2e8f0' }, ticks: { color: '#64748b' } }, 
                    x: { grid: { display: false }, ticks: { color: '#64748b' } } 
                },
                plugins: { legend: { labels: { color: '#1e293b', font: { weight: 'bold' } } } }
            }
        });

        // 渲染輿情分析甜甜圈圖表
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
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#1e293b', font: { weight: 'bold' }, padding: 15 } }
                }
            }
        });

    } catch (err) {
        console.error('載入分析數據失敗', err);
    }
}
