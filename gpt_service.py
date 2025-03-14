import os
import logging
import httpx
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수에서 프록시 제거
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

# .env 파일에서 환경 변수 로드
load_dotenv()

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

class GPTService:
    def __init__(self):
        # OpenAI API 키 설정
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            logger.error("OPENAI_API_KEY가 설정되지 않았습니다.")
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

        # OpenAI 클라이언트 초기화 시 디버그 로깅 및 예외 처리
        try:
            logger.debug("OpenAI 클라이언트 초기화 시도")
            
            # httpx 클라이언트 명시적 설정 (프록시 없음)
            http_client = httpx.Client(
                transport=httpx.HTTPTransport(
                    retries=2, 
                )
            )
            
            # 클라이언트 초기화
            self.client = OpenAI(
                api_key=self.api_key,
                http_client=http_client
            )
            
            logger.debug("OpenAI 클라이언트 초기화 성공")
        except Exception as e:
            logger.error(f"OpenAI 클라이언트 초기화 중 예외 발생: {str(e)}")
            # 추가 디버깅 정보 출력
            import traceback
            logger.error(traceback.format_exc())
            raise

        # 기본 모델 설정
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        logger.info(f"GPTService 초기화 완료: 모델={self.model}")

    def get_chat_response(self, user_message, language="en"):
        """
        GPT 모델을 사용하여 채팅 응답을 가져옵니다.
        
        Args:
            user_message (str): 사용자 메시지
            language (str): 언어 코드 (en: 영어, ja: 일본어)
            
        Returns:
            dict: 응답 데이터 (응답 텍스트, 핵심 단어, 예문 등)
        """
        try:
            logger.info(f"GPT API 호출 시작: 언어={language}, 메시지={user_message[:50] if len(user_message) > 50 else user_message}...")

            # 시스템 메시지 설정 (언어에 따라 다르게)
            if language == "en":
                system_message = (
                    "You are a helpful English conversation partner. "
                    "After responding to the user's message, identify 3 key words or phrases from your response. "
                    "For each word, provide the Korean meaning and 2 example sentences using that word. "
                    "Format your response as: "
                    "[Your normal response] "
                    "VOCABULARY_SECTION: "
                    "1. [word]: [Korean meaning] "
                    "- Example 1: [example] "
                    "- Example 2: [example] "
                    "2. [word]: [Korean meaning] - [examples...] "
                    "3. [word]: [Korean meaning] - [examples...]"
                )
            elif language == "ja":
                system_message = (
                    "あなたは役立つ日本語の会話パートナーです。"
                    "ユーザーのメッセージに応答した後、あなたの応答から3つのキーワードまたはフレーズを特定します。"
                    "各単語について、韓国語の意味とその単語を使用した2つの例文を提供してください。"
                    "次の形式で応答してください: "
                    "[通常の応答] "
                    "語彙セクション: "
                    "1. [単語]: [韓国語の意味] - 例文1: [例文] - 例文2: [例文] "
                    "2. [単語]: [韓国語の意味] - [例文...] "
                    "3. [単語]: [韓国語の意味] - [例文...]"
                )
            else:
                system_message = (
                    "You are a helpful conversation partner. "
                    "Please respond naturally to the user's message."
                )
            
            # GPT API 호출 (최신 버전 문법)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # 응답 추출
            response_text = response.choices[0].message.content
            usage = response.usage.total_tokens if hasattr(response, 'usage') else None
            
            logger.info(f"GPT API 응답 성공: 토큰 사용량={usage}")

            # 응답 데이터 구성
            result = {
                "answer": response_text,
                "model": self.model,
                "usage": {"total_tokens": usage} if usage else None
            }

            return result
            
        except Exception as e:
            logger.error(f"GPT API 호출 중 오류 발생: {str(e)}")
            # 추가 디버깅 정보 출력
            import traceback
            logger.error(traceback.format_exc())
            raise e
    
    def format_learning_response(self, response_text, language="en"):
        """
        GPT 응답에서 일반 대화와 학습 콘텐츠(단어, 의미, 예문 등)를 분리합니다.
        
        Args:
            response_text (str): GPT 응답 텍스트
            language (str): 언어 코드
            
        Returns:
            dict: 분리된 응답 데이터
        """
        try:
            # 영어 응답 처리
            if language == "en":
                if "VOCABULARY_SECTION:" in response_text:
                    parts = response_text.split("VOCABULARY_SECTION:", 1)
                    conversation = parts[0].strip()
                    vocabulary = parts[1].strip() if len(parts) > 1 else ""
                else:
                    conversation = response_text
                    vocabulary = ""

            # 일본어 응답 처리
            elif language == "ja":
                if "語彙セクション:" in response_text:
                    parts = response_text.split("語彙セクション:", 1)
                    conversation = parts[0].strip()
                    vocabulary = parts[1].strip() if len(parts) > 1 else ""
                else:
                    conversation = response_text
                    vocabulary = ""

            # 그 외 언어는 그대로 반환
            else:
                conversation = response_text
                vocabulary = ""

            return {
                "conversation": conversation,
                "vocabulary": vocabulary
            }

        except Exception as e:
            logger.error(f"응답 포맷팅 중 오류 발생: {str(e)}")
            # 추가 디버깅 정보 출력
            import traceback
            logger.error(traceback.format_exc())
            return {
                "conversation": response_text,
                "vocabulary": ""
            }