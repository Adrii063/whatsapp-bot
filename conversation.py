class ConversationManager:
    def __init__(self):
        self.user_conversations = {}

    def add_message(self, user_id, role, content):
        if user_id not in self.user_conversations:
            self.user_conversations[user_id] = []

        self.user_conversations[user_id].append({"role": role, "content": content})
        self.user_conversations[user_id] = self.user_conversations[user_id][-10:]  # Mantiene solo 10 mensajes

    def get_history(self, user_id):
        return self.user_conversations.get(user_id, [])

conversation_manager = ConversationManager()