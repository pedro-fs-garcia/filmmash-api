# class SessionService:
#     def __init__(self, session_repo, token_service):
#         self.repo = session_repo
#         self.token_service = token_service

#     async def refresh_access_token(self, refresh_token: str) -> str:
#         session = await self.repo.get_by_token(refresh_token)

#         if not session.is_active():
#             raise SessionExpiredException()

#         session.mark_used()
#         await self.repo.save(session)

#         return self.token_service.create_access_token(session.user_id)
