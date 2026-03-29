from fastapi import HTTPException

class GitHubAPIError(HTTPException):
    def __init__(self, detail: str, status_code: int = 500):
        super().__init__(status_code=status_code, detail=detail)

class OllamaAPIError(HTTPException):
    def __init__(self, detail: str, status_code: int = 500):
        super().__init__(status_code=status_code, detail=detail)

class RepositoryNotFoundError(HTTPException):
    def __init__(self, detail: str = "Repository not found."):
        super().__init__(status_code=404, detail=detail)

class AnalysisError(HTTPException):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)
