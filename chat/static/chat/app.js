
const form = document.querySelector(".input-area");
const input = form.querySelector('input[name="prompt"]');
const button = form.querySelector("button");
const chatArea = document.querySelector(".chat-area");
// 保存済みの会話を開いたら、一番下を表示する
chatArea.scrollTop = chatArea.scrollHeight;

// メッセージを画面に追加する
function addMessage(role, content) {
    const message = document.createElement("div");
    message.className = `message ${role}`;
    message.textContent = content;
    message.style.whiteSpace = "pre-wrap";

    chatArea.appendChild(message);
    chatArea.scrollTop = chatArea.scrollHeight;

    return message;
}

// フォームの送信処理
form.addEventListener("submit", async (event) => {
    event.preventDefault();


    const prompt = input.value.trim();
    if (!prompt || button.disabled) return;

    // 最初の挨拶があれば削除する
    const welcomeMessage = chatArea.querySelector(".welcome-message");
    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    const formData = new FormData(form);


    input.value = "";
    input.disabled = true;
    button.disabled = true;
    button.textContent = "生成中...";

    addMessage("user", prompt);

    const aiMessage = addMessage("assistant", "AIが考えています...");

    try {
        const response = await fetch("/stream/", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        if (!response.body) {
            throw new Error("ストリーミングに対応していません");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        let answer = "";

        // AIの回答を少しずつ受け取る
        while (true) {
            const { done, value } = await reader.read();

            if (done) break;

            answer += decoder.decode(value, { stream: true });

            aiMessage.textContent = answer;
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        answer += decoder.decode();
        aiMessage.textContent = answer || "回答がありませんでした。";

        // AIの回答完了後、会話一覧を更新する

        // 会話履歴の更新に失敗しても、AIの回答は残す
        try {
            const pageResponse = await fetch("/", { cache: "no-store" });

            if (pageResponse.ok) {
                const html = await pageResponse.text();
                const doc = new DOMParser().parseFromString(html, "text/html");

                const newHistory = doc.querySelector(".conversation-history ul");
                const currentHistory = document.querySelector(".conversation-history ul");

                if (newHistory && currentHistory) {
                    currentHistory.innerHTML = newHistory.innerHTML;
                }
            }
        } catch (error) {
            console.warn("会話履歴の更新に失敗:", error);
        }
    } catch (error) {
        aiMessage.textContent = `通信エラー: ${error.message}`;
    } finally {
        input.disabled = false;
        button.disabled = false;
        button.textContent = "送信";
        input.focus();
    }
});
