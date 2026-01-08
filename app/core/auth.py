from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from ..schemas.users import TokenData
from dotenv import load_dotenv
import os
load_dotenv()

pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2=OAuth2PasswordBearer(tokenUrl="/user/login")

SECRET_KEY = os.getenv("KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 30

class Hash():
    
    @staticmethod
    def bcrypt(password: str) -> str:
        """
        Hashea una contraseña de forma segura para bcrypt.
        Bcrypt tiene un límite de 72 bytes, así que truncamos si es necesario.
        """
        # Bcrypt soporta máximo 72 bytes
        MAX_BCRYPT_BYTES = 72
        
        # Verificar longitud en bytes
        password_bytes = password.encode('utf-8')
        
        if len(password_bytes) > MAX_BCRYPT_BYTES:
            # Truncar a 72 bytes manteniendo caracteres válidos
            truncated_bytes = password_bytes[:MAX_BCRYPT_BYTES]
            
            # Intentar decodificar de vuelta a string
            try:
                # Decodificar ignorando bytes incompletos al final
                truncated_password = truncated_bytes.decode('utf-8', 'ignore')
                # Si quedó vacío, usar un fallback
                if not truncated_password:
                    # Tomar primeros 50 caracteres como fallback seguro
                    truncated_password = password[:50]
            except UnicodeDecodeError:
                # Si falla la decodificación, usar slice simple
                truncated_password = password[:50]
            
            # Usar la versión truncada
            password = truncated_password
        
        return pwd_context.hash(password)
    
    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_DURATION)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def verify_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str=payload.get("sub")
        if email is None:
            raise credential_exception
        return TokenData(email=email)
    except JWTError:
        raise credential_exception


