// ==UserScript==
// @name         Gemini Auto Thay Đồ 2K (Dự án TikTok)
// @namespace    https://github.com/namnv
// @version      1.0
// @description  Tự động hóa thay đồ cho người mẫu trên gemini.google.com chuẩn 2K không lo bị gắn cờ unusual
// @author       Antigravity
// @match        https://gemini.google.com/*
// @grant        GM_xmlhttpRequest
// @connect      127.0.0.1
// @connect      localhost
// @run-at       document-idle
// ==/UserScript==

(function () {
    'use strict';

    const BRIDGE_URL = "http://127.0.0.1:8765";
    let isRunning = false;

    // --- 1. Tạo giao diện điều khiển nổi (Floating Panel) ---
    function createUI() {
        if (document.getElementById("gemini-auto-panel")) return;

        const panel = document.createElement("div");
        panel.id = "gemini-auto-panel";
        panel.style.cssText = `
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 999999;
            background: #1e1f20;
            color: #e3e3e3;
            border: 1px solid #444746;
            border-radius: 12px;
            padding: 16px;
            width: 320px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            font-family: Google Sans, sans-serif, system-ui;
            font-size: 13px;
        `;

        panel.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <b style="font-size:14px; color:#c4eed0;">✨ Auto Thay Đồ 2K</b>
                <span id="auto-status" style="padding:2px 8px; border-radius:10px; background:#333; font-size:11px;">Sẵn sàng</span>
            </div>
            <div id="auto-log" style="background:#131314; padding:8px; border-radius:6px; height:80px; overflow-y:auto; font-family:monospace; font-size:11px; margin-bottom:12px; border:1px solid #333;">
                [Bridge] Sẵn sàng kết nối...
            </div>
            <div style="display:flex; gap:8px;">
                <button id="btn-start" style="flex:1; padding:8px; background:#0b57d0; color:white; border:none; border-radius:6px; font-weight:600; cursor:pointer;">▶ Chạy Auto</button>
                <button id="btn-stop" style="flex:1; padding:8px; background:#37393b; color:#e3e3e3; border:none; border-radius:6px; cursor:pointer;" disabled>⏹ Dừng</button>
            </div>
        `;

        document.body.appendChild(panel);

        document.getElementById("btn-start").onclick = startAutomation;
        document.getElementById("btn-stop").onclick = stopAutomation;
    }

    function log(msg) {
        console.log("[Auto Thay Đồ]", msg);
        const el = document.getElementById("auto-log");
        if (el) {
            el.innerHTML += `<div>${msg}</div>`;
            el.scrollTop = el.scrollHeight;
        }
    }

    function setStatus(text, bg = "#333") {
        const el = document.getElementById("auto-status");
        if (el) {
            el.innerText = text;
            el.style.background = bg;
        }
    }

    // --- 2. Tiện ích giao tiếp với Bridge Server & Trình duyệt ---
    function fetchJSON(url, options = {}) {
        return new Promise((resolve, reject) => {
            GM_xmlhttpRequest({
                method: options.method || "GET",
                url: url,
                headers: options.headers || {},
                data: options.body || null,
                onload: (res) => {
                    if (res.status >= 200 && res.status < 300) {
                        try { resolve(JSON.parse(res.responseText)); } catch (e) { resolve(res.responseText); }
                    } else {
                        reject(new Error(`Lỗi HTTP ${res.status}: ${res.responseText}`));
                    }
                },
                onerror: reject
            });
        });
    }

    function fetchBlob(url) {
        return new Promise((resolve, reject) => {
            GM_xmlhttpRequest({
                method: "GET",
                url: url,
                responseType: "blob",
                onload: (res) => resolve(res.response),
                onerror: reject
            });
        });
    }

    const wait = (ms) => new Promise(r => setTimeout(r, ms));

    // --- 3. Tương tác DOM tự nhiên của Gemini ---
    async function openNewChat() {
        log("Mở phiên chat mới...");
        const newChatBtn = document.querySelector('button[aria-label*="New chat"], button[aria-label*="Trò chuyện mới"], a[href="/app"]');
        if (newChatBtn) {
            newChatBtn.click();
            await wait(2500);
        } else {
            window.location.href = "https://gemini.google.com/app";
            await wait(3000);
        }
    }

    async function uploadImages(imageUrls) {
        log("Đang tải 4 ảnh từ local bridge...");
        setStatus("Tải 4 ảnh...", "#8c5b00");

        const files = [];
        for (let i = 0; i < imageUrls.length; i++) {
            const blob = await fetchBlob(imageUrls[i]);
            const filename = `image_${i + 1}.png`;
            files.push(new File([blob], filename, { type: blob.type || "image/png" }));
        }

        // Mở menu công cụ nếu input file chưa lộ diện
        let fileInput = document.querySelector('input[type="file"][accept*="image"]');
        if (!fileInput) {
            const plusBtn = document.querySelector('button[aria-label*="Upload"], button[aria-label*="Công cụ"], button[aria-label*="tools"], button[aria-label*="Thêm"]');
            if (plusBtn) {
                plusBtn.click();
                await wait(1000);
                fileInput = document.querySelector('input[type="file"][accept*="image"]');
            }
        }

        if (!fileInput) {
            throw new Error("Không tìm thấy input tải ảnh của Gemini!");
        }

        // Đính kèm 4 file qua DataTransfer
        const dt = new DataTransfer();
        files.forEach(f => dt.items.add(f));
        fileInput.files = dt.files;
        fileInput.dispatchEvent(new Event('change', { bubbles: true }));

        log("Đã đính kèm 4 ảnh, đợi Gemini tải lên...");
        await wait(6000); // Đợi thumbnails hiện đầy đủ
    }

    async function sendPrompt(promptText) {
        log("Đang nhập prompt...");
        setStatus("Gửi prompt...", "#0b57d0");

        const editor = document.querySelector('rich-textarea div[contenteditable="true"], div[role="textbox"] p, div[contenteditable="true"]');
        if (!editor) throw new Error("Không tìm thấy ô nhập tin nhắn Gemini!");

        editor.focus();
        // Giả lập nhập văn bản
        document.execCommand('selectAll', false, null);
        document.execCommand('insertText', false, promptText);
        editor.dispatchEvent(new Event('input', { bubbles: true }));

        await wait(1000);

        const sendBtn = document.querySelector('button[aria-label*="Send message"], button[aria-label*="Gửi tin nhắn"], button.send-button');
        if (!sendBtn || sendBtn.getAttribute("aria-disabled") === "true") {
            throw new Error("Nút gửi chưa sẵn sàng!");
        }
        sendBtn.click();
        log("Đã gửi! Đang chờ Gemini gen ảnh...");
    }

    async function waitForImageAndDownload2K(startTime) {
        setStatus("Đang gen ảnh 2K...", "#137333");
        const maxWait = 180000; // tối đa 3 phút
        const start = Date.now();

        while (Date.now() - start < maxWait) {
            if (!isRunning) return null;

            // Tìm nút download full-size
            const downloadBtn = document.querySelector('button[aria-label*="Download full size"], button[aria-label*="kích thước đầy đủ"], button[aria-label*="Tải xuống hình ảnh có kích thước đầy đủ"]');
            if (downloadBtn) {
                log("Đã có ảnh! Bấm tải full size 2K...");
                downloadBtn.click();
                await wait(4000);
                return true;
            }

            // Kiểm tra nếu Gemini từ chối hoặc lỗi
            const errorText = document.body.innerText;
            if (errorText.includes("Your limit resets at") || errorText.includes("Hạn ngạch của bạn sẽ đặt lại")) {
                throw new Error("Tài khoản đã hết hạn mức Gemini hôm nay!");
            }

            await wait(4000);
        }
        throw new Error("Quá thời gian chờ tạo ảnh (Timeout 3 phút)");
    }

    // --- 4. Vòng lặp tự động hóa chính ---
    async function startAutomation() {
        if (isRunning) return;
        isRunning = true;

        document.getElementById("btn-start").disabled = true;
        document.getElementById("btn-stop").disabled = false;

        try {
            while (isRunning) {
                const startTime = Date.now() / 1000;
                log("Đang lấy task tiếp theo từ Bridge...");
                const task = await fetchJSON(`${BRIDGE_URL}/api/next-task`);

                if (!task.has_task) {
                    log("🎉 Đã hoàn thành toàn bộ ảnh trong bộ!");
                    setStatus("Hoàn tất!", "#137333");
                    break;
                }

                log(`Bắt đầu xử lý: ${task.index}`);
                setStatus(`Đang làm ${task.index}`, "#0b57d0");

                // Đảm bảo mở trang chat sạch
                await openNewChat();

                // 1. Tải và upload 4 ảnh
                await uploadImages(task.images);

                // 2. Nhập và gửi prompt
                await sendPrompt(task.prompt);

                // 3. Chờ tạo ảnh và bấm Download Full size (2K)
                await waitForImageAndDownload2K(startTime);

                // 4. Báo Bridge Server gom file từ ~/Downloads vào generated/
                log("Báo server gom ảnh từ Downloads...");
                await fetchJSON(`${BRIDGE_URL}/api/collect`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ index: task.index, since: startTime })
                });

                log(`✅ Đã xong và lưu ${task.index}! Nghỉ 10s trước ảnh tiếp...`);
                await wait(10000); // Giãn cách 10s để hoàn toàn tự nhiên
            }
        } catch (err) {
            log(`❌ Lỗi: ${err.message}`);
            setStatus("Bị lỗi", "#b3261e");
        } finally {
            stopAutomation();
        }
    }

    function stopAutomation() {
        isRunning = false;
        document.getElementById("btn-start").disabled = false;
        document.getElementById("btn-stop").disabled = true;
        setStatus("Đã dừng", "#333");
        log("Đã dừng chu trình.");
    }

    // Tự động khởi tạo UI khi trang tải xong
    setTimeout(createUI, 2000);
})();
