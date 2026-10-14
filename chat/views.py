
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
from django.http import JsonResponse, StreamingHttpResponse
import json
from urllib.request import Request, urlopen
from django.shortcuts import render, redirect



@login_required
def index(request):
    # 現在の会話IDを取得
    conversation_id = request.session.get("conversation_id")

    # SQLiteから会話履歴を取得
    messages = list(
        Message.objects.filter(conversation_id=conversation_id)
        .order_by("id")
        .values("role", "content")
    )

    # チャット画面を表示
    return render(request, "chat/index.html", {
        "messages": messages,
        "error": "",
        "conversations": Conversation.objects.order_by("-id"),
        "current_conversation_id": conversation_id,
    })




@login_required
def stream_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "POSTのみ対応"}, status=405)

    prompt = request.POST.get("prompt", "").strip()

    if not prompt:
        return JsonResponse({"error": "質問が空です"}, status=400)



    
    
    # 現在の会話を取得する
    conversation_id = request.session.get("conversation_id")

    conversation = (
        Conversation.objects.filter(id=conversation_id).first()
        if conversation_id else None
    )

    # 会話が存在しなければ作成する
    if conversation is None:
        conversation = Conversation.objects.create(
            title="新しい会話"
        )
        request.session["conversation_id"] = conversation.id
        
    # データベースから直近10件の履歴を取得
    messages = list(
        conversation.messages.order_by("id").values("role", "content")
    )[-10:]


    
    user_message = {"role": "user", "content": prompt}

    data = {
        "model": "qwen3:4b-instruct",
        "messages": [
            {"role": "system", "content": "必ず日本語で回答してください。"},
            *messages,
            user_message
        ],
        "stream": True
    }

    req = Request(
        "http://localhost:11434/api/chat",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )



    def generate():
        parts = []

        try:
            with urlopen(req, timeout=240) as response:
                for line in response:
                    if not line.strip():
                        continue

                    chunk = json.loads(line)
                    text = chunk.get("message", {}).get("content", "")

                    if text:
                        parts.append(text)
                        yield text


            
            # 質問をデータベースに保存
            Message.objects.create(
                conversation=conversation,
                role="user",
                content=prompt
            )

            # AIの回答をデータベースに保存
            Message.objects.create(
                conversation=conversation,
                role="assistant",
                content="".join(parts)
            )
            
            # 最初の質問を会話タイトルにする
            if conversation.title == "新しい会話":
                conversation.title = prompt[:30]
                conversation.save(update_fields=["title"])



        except Exception as e:
            yield f"\n通信エラー: {e}"

    return StreamingHttpResponse(
        generate(),
        content_type="text/plain; charset=utf-8"
    )

@login_required
def new_chat(request):
    if request.method == "POST":
        # データベースに新しい会話を作成
        conversation = Conversation.objects.create(
            title="新しい会話"
        )

        # 現在の会話IDをセッションに保存
        request.session["conversation_id"] = conversation.id

        # 古いセッションの会話履歴をクリア
        request.session.pop("messages", None)

    return redirect("index")

@login_required
def open_chat(request, conversation_id):
    if request.method == "POST":
        conversation = Conversation.objects.filter(
            id=conversation_id
        ).first()

        if conversation:
            request.session["conversation_id"] = conversation.id
            request.session.pop("messages", None)

    return redirect("index")

@login_required
def delete_chat(request, conversation_id):
    if request.method == "POST":
        conversation = Conversation.objects.filter(
            id=conversation_id
        ).first()

        if conversation:
            conversation.delete()

            # 開いている会話を削除した場合
            if request.session.get("conversation_id") == conversation_id:
                request.session.pop("conversation_id", None)

    return redirect("index")

@login_required
def rename_chat(request, conversation_id):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()

        if title:
            Conversation.objects.filter(
                id=conversation_id
            ).update(title=title[:100])

    return redirect("index")

