from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import asyncio
from openai_api import detect_response_type, generate_text, generate_image_from_text
from io import BytesIO
from datetime import datetime

app = FastAPI()

# 요청으로 들어오는 데이터의 구조를 정의하는 Pydantic 모델
class PromptRequest(BaseModel):
    username: str  # 사용자의 고유 ID
    prompt: str   # 사용자가 입력한 질문 또는 명령어

# 텍스트 또는 이미지 생성을 위한 엔드포인트 정의
@app.post("/generate")
async def generate_route(data: PromptRequest):
    username = data.username
    prompt = data.prompt

    if not prompt:
        raise HTTPException(status_code=400, detail="잘못된 입력 값 입니다.")

    # 프롬프트를 분석하여 이미지 생성인지 텍스트 생성인지 판별
    response_type = detect_response_type(prompt)

    try:
        if response_type == 'image':
            # 이미지 생성 작업 비동기 처리 시작
            image_task = asyncio.create_task(generate_image_from_text(username, prompt))
            
            # 텍스트 생성 (동시에 처리되지 않고, 차례로 처리됨)
            generated_text = await generate_text(username, prompt)

            # 이미지 생성 완료 대기
            image = await image_task
            
            # 이미지 생성이 성공적으로 완료된 경우, 이미지를 반환
            if image:
                img_io = BytesIO()
                image.save(img_io, 'PNG')
                img_io.seek(0)
                return StreamingResponse(img_io, media_type="image/png")
            else:
                return create_response("GENERATED_FAILED", "이미지 생성에 실패했습니다.", 500, None)
        else:
            generated_text = await generate_text(username, prompt)
            return JSONResponse(content={"generated_text": generated_text})
    
    except Exception as e:
            print(f"An error occurred: {e}")
            return create_response("GENERATED_FAILED", str(e), 500, None)

def create_response(message, details, http_status, data):
    response = {
        "timeStamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "code": http_status,
        "message": message,
        "details": details,
        "data": data
    }
    return JSONResponse(content=response, status_code=200)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:app", host='0.0.0.0', port=5001)
