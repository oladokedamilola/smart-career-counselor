
from collections import defaultdict
import json
import uuid
from .models import ChatSession, ChatHistory
from django.views.decorators.http import require_POST

from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from users.models import CareerProfile
from .llm import *
from .search import search_web
from .models import ChatSession, ChatHistory
import json
import uuid
import logging

from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import ChatSession, ChatHistory
from users.models import CareerProfile
from .llm import query_llm
from .search import search_web

import json
import logging

logger = logging.getLogger(__name__)


from django.utils import timezone

def group_chats_by_time(sessions):
    grouped = {
        "Today": [],
        "Yesterday": [],
        "Last 7 Days": [],
        "Last Month": [],
        "Last 3 Months": [],
        "Older": [],
    }

    now = timezone.now()  # Use timezone-aware datetime
    for session in sessions:
        created = session.created_at
        delta = now - created

        if delta.days == 0:
            grouped["Today"].append(session)
        elif delta.days == 1:
            grouped["Yesterday"].append(session)
        elif delta.days <= 7:
            grouped["Last 7 Days"].append(session)
        elif delta.days <= 30:
            grouped["Last Month"].append(session)
        elif delta.days <= 90:
            grouped["Last 3 Months"].append(session)
        else:
            grouped["Older"].append(session)

    return grouped



@csrf_exempt
@login_required
def chat_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"reply": "⚠️ Please enter a message."}, status=400)

            # Check for existing session
            session_id = request.session.get('chat_session_id')
            session = None

            if session_id:
                session = ChatSession.objects.filter(id=session_id, user=request.user).first()

            if not session:
                try:
                    generated_title = generate_chat_title(user_message)
                    if not generated_title or "❗" in generated_title:
                        generated_title = user_message[:40]
                except Exception:
                    generated_title = user_message[:40]

                session = ChatSession.objects.create(
                    user=request.user,
                    title=generated_title
                )
                request.session['chat_session_id'] = str(session.id)

            # Load user profile
            try:
                profile = CareerProfile.objects.get(user=request.user)
            except CareerProfile.DoesNotExist:
                return JsonResponse({
                    "reply": "⚠️ No career profile found. Please complete your profile to get personalized advice."
                }, status=400)

            # Construct LLM prompt
            prompt = f"""
You are a helpful career advisor AI. Consider the user profile and question below and provide tailored career advice.

User Profile:
- Education: {profile.highest_education} in {profile.field_of_study}
- University: {profile.university}
- Skills: {profile.skills}
- Interests: {profile.interests}

User asks: {user_message}
Respond with relevant career guidance.
"""

            # Query LLM
            bot_reply = query_llm(prompt)
            if not bot_reply:
                bot_reply = "I'm sorry, I couldn't generate a response. Please try again."

            # Optionally add resources
            if any(keyword in user_message.lower() for keyword in ["course", "resource", "learn"]):
                links = search_web(user_message)
                if links:
                    bot_reply += "\n\n📚 Helpful Resources:\n" + "\n".join(links)

            # Save chat history
            ChatHistory.objects.create(
                session=session,
                user=request.user,
                user_message=user_message,
                bot_reply=bot_reply
            )

            return JsonResponse({
                "reply": bot_reply,
                "session_id": str(session.id),
                "session_title": session.title
            })

        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            return JsonResponse({"reply": f"❗ An error occurred: {str(e)}"}, status=500)

    elif request.method == "GET":
        # Load sessions and group history by session_id
        chat_sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')

        # Get current session ID and details
        current_session_id = request.session.get('chat_session_id')
        active_session = (
            ChatSession.objects.filter(id=current_session_id, user=request.user).first()
            if current_session_id else None
        )
        sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
        grouped_sessions = group_chats_by_time(sessions)


        full_session = (
            active_session.messages.all().order_by('timestamp')
            if active_session else []
        )

        return render(request, 'chatbot/chatbot.html', {
            'chat_sessions': chat_sessions,
            'full_session': full_session,
            'sidebar_mode': 'chat',
            'current_session': str(active_session.id) if active_session else "",
            'current_chat': active_session, 
            'grouped_sessions': grouped_sessions,
 
        })

    return HttpResponseNotAllowed(['GET', 'POST'])


# @csrf_exempt
# @login_required
# def chat_view(request):
#     if request.method == "POST":
#         # ✅ TEMPORARY test response
#         return JsonResponse({"reply": "This is a test response."})

#     elif request.method == "GET":
#         # ✅ Render chat page as usual
#         sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
#         current_session_id = request.session.get('chat_session_id')
#         active_session = None
#         full_session = []

#         if current_session_id:
#             active_session = ChatSession.objects.filter(id=current_session_id, user=request.user).first()
#             if active_session:
#                 full_session = active_session.messages.all().order_by('timestamp')

#         return render(request, 'chatbot/chatbot.html', {
#             'chat_sessions': sessions,
#             'full_session': full_session,
#             'sidebar_mode': 'chat',
#             'current_session': active_session
#         })

#     return HttpResponseNotAllowed(['GET', 'POST'])

@login_required
def start_new_chat(request):
    request.session['chat_session_id'] = str(uuid.uuid4())
    return redirect('chat')


@require_POST
@login_required
def send_first_message(request):
    data = json.loads(request.body)
    message_text = data.get('message')

    if not message_text:
        return JsonResponse({'error': 'Message is empty'}, status=400)

    # Create session
    session = ChatSession.objects.create(user=request.user, title="Untitled")

    # Save initial message
    ChatHistory.objects.create(session=session, message=message_text, is_user=True)

    return JsonResponse({
        'session_id': str(session.id),
        'title': session.title
    })

@login_required
def load_session(request, session_id):
    request.session['chat_session_id'] = str(session_id)

    chat_sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
    grouped_sessions = group_chats_by_time(sessions)


    full_session = ChatHistory.objects.filter(
        user=request.user,
        session_id=session_id
    ).order_by('timestamp')

    return render(request, 'chatbot/chatbot.html', {
        'chat_sessions': chat_sessions,
        'full_session': full_session,
        'sidebar_mode': 'chat',
        'current_session': str(session_id),
        'current_chat': ChatSession.objects.get(id=session_id, user=request.user), 
        'grouped_sessions': grouped_sessions,
    })



@require_POST
@login_required
def rename_session(request, session_id):
    new_title = request.POST.get('title', '').strip()
    session = ChatSession.objects.get(id=session_id, user=request.user)
    if new_title:
        session.title = new_title
        session.save()
    return redirect('chat')

@require_POST
@login_required
def delete_session(request, session_id):
    ChatSession.objects.filter(id=session_id, user=request.user).delete()
    if request.session.get('chat_session_id') == str(session_id):
        del request.session['chat_session_id']
    return redirect('chat')




# @csrf_exempt
# @login_required
# def chat_view(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         user_message = data.get("message", "")

#         session_id = request.session.get('chat_session_id')
#         session = None

#         if session_id:
#             try:
#                 session = ChatSession.objects.get(id=session_id, user=request.user)
#             except ChatSession.DoesNotExist:
#                 session = None

#         if not session:
#             # First message = new session
#             session = ChatSession.objects.create(
#                 user=request.user,
#                 title=user_message[:40]  # First message becomes title (truncate for DB)
#             )
#             request.session['chat_session_id'] = str(session.id)

#         # Get profile
#         profile = CareerProfile.objects.get(user=request.user)

#         prompt = f"""
#         User Profile:
#         - Education: {profile.highest_education} in {profile.field_of_study}
#         - University: {profile.university}
#         - Skills: {profile.skills}
#         - Interests: {profile.interests}

#         User asks: {user_message}
#         Provide personalized career advice based on the profile above.
#         """
#         bot_reply = query_llm(prompt)

#         if "course" in user_message.lower() or "resource" in user_message.lower():
#             links = search_web(user_message)
#             bot_reply += "\nHelpful resources:\n" + "\n".join(links)

#         ChatHistory.objects.create(
#             session=session,
#             user=request.user,
#             user_message=user_message,
#             bot_reply=bot_reply
#         )

#         return JsonResponse({"reply": bot_reply})

#     # GET: render page
#     sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
#     current_session_id = request.session.get('chat_session_id')
#     active_session = None
#     full_session = []

#     if current_session_id:
#         active_session = ChatSession.objects.filter(id=current_session_id, user=request.user).first()
#         if active_session:
#             full_session = active_session.messages.all().order_by('timestamp')

#     return render(request, 'chatbot/chatbot.html', {
#         'chat_sessions': sessions,
#         'full_session': full_session,
#         'sidebar_mode': 'chat',
#         'current_session': active_session
#     })
