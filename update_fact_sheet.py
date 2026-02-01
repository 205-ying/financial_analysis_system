"""
批量更新 fact_sheet.md 的证据

将"⚠️待补证据"替换为实际代码证据
"""

# 证据字典
EVIDENCE_MAP = {
    # A2 系统定位
    "A2_data_import": '''  - **证据1（数据导入模块）**: `backend/alembic/versions/0003_import_jobs.py`
    ```python
    # 导入任务表：支持多源（Excel/CSV/API）、多目标（订单/费用/门店）
    source_type = sa.Column(sa.Enum('EXCEL', 'CSV', 'API', name='sourcetype'), nullable=False)
    target_type = sa.Column(sa.Enum('ORDER', 'EXPENSE_RECORD', 'STORE', 'EXPENSE_TYPE', name='targettype'), nullable=False)
    status = sa.Column(sa.Enum('PENDING', 'RUNNING', 'SUCCESS', 'FAILED', name='importstatus'), nullable=False)
    ```
  - **证据2（审计留痕）**: `backend/app/services/audit_log_service.py`
    ```python
    # 审计日志服务：记录关键操作
    async def create_log(
        self,
        action: str,                    # 操作类型
        username: str,                  # 操作用户名
        user_id: Optional[int] = None,  # 用户ID
        resource_type: Optional[str] = None,  # 资源类型
        ip_address: Optional[str] = None,     # 客户端IP
    )
    ```''',
    
    # A3 目标用户
    "A3_superuser": '''  - **证据1（超级用户字段）**: `backend/app/models/user.py`
    ```python
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        comment="是否超级用户"
    )
    ```
  - **证据2（权限兜底）**: `backend/app/api/deps.py`
    ```python
    async def check_permission(user: User, permission_code: str, db: AsyncSession):
        # 超级用户拥有所有权限
        if user.is_superuser:
            return True
    ```''',
    
    # A4 审计日志
    "A4_audit": '''  - **证据（审计日志）**: `backend/app/services/audit_log_service.py`
    ```python
    async def create_log(
        self,
        action: str,        # 操作类型（CREATE/UPDATE/DELETE/EXPORT等）
        username: str,      # 操作用户名
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,  # 资源类型
        resource_id: Optional[int] = None,    # 资源ID
        detail: Optional[dict] = None,        # 操作详情
        ip_address: Optional[str] = None,     # 客户端IP
        user_agent: Optional[str] = None,     # User-Agent
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> AuditLog
    ```''',
    
    # A5 数据权限
    "A5_data_scope": '''  - **证据（数据权限算法）**: `backend/app/services/data_scope_service.py`
    ```python
    async def get_accessible_store_ids(db: AsyncSession, user: User) -> Optional[List[int]]:
        \"\"\"
        获取用户可访问的门店ID列表
        
        规则：
        - 超级管理员：返回 None（可访问全部）
        - 没有门店权限记录：返回 None（可访问全部，向后兼容）
        - 有门店权限记录：返回授权的门店ID列表
        \"\"\"
        if user.is_superuser:
            return None  # 超级管理员无限制
        
        # 查询用户的门店权限
        result = await db.execute(
            select(UserStorePermission.store_id)
            .where(UserStorePermission.user_id == user.id)
        )
        store_ids = [row[0] for row in result.all()]
        
        if not store_ids:
            return None  # 向后兼容
        
        return store_ids
    ```''',
    
    # B1 FastAPI
    "B1_fastapi": '''  - **证据（FastAPI初始化）**: `backend/app/main.py`
    ```python
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    
    # 创建FastAPI应用
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan
    )
    
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    
    # 注册全局异常处理器
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # 注册路由
    app.include_router(api_router, prefix="/api/v1")
    ```''',
    
    # B3 JWT
    "B3_jwt": '''  - **证据1（JWT配置）**: `backend/app/core/config.py`
    ```python
    jwt_secret_key: str = Field(
        default="your-super-secret-jwt-key-change-this-in-production",
        description="JWT 密钥"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT 算法")
    jwt_expire_minutes: int = Field(default=30, description="JWT 过期时间（分钟）")
    jwt_refresh_expire_days: int = Field(default=7, description="刷新令牌过期时间（天）")
    ```
  - **证据2（JWT编解码）**: `backend/app/core/security.py`
    ```python
    def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        \"\"\"创建 JWT 访问令牌\"\"\"
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt
    
    def decode_access_token(token: str) -> Optional[dict[str, Any]]:
        \"\"\"解码 JWT 令牌\"\"\"
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError:
            return None
    ```''',
    
    # B3 密码哈希
    "B3_password": '''  - **证据（密码哈希算法）**: `backend/app/core/security.py`
    ```python
    import bcrypt
    
    def hash_password(password: str) -> str:
        \"\"\"使用 bcrypt 哈希密码\"\"\"
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        \"\"\"验证密码\"\"\"
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    ```
  - **证据（数据库存储）**: `backend/app/models/user.py`
    ```python
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码哈希"
    )
    ```''',
}

print("证据映射已准备，共", len(EVIDENCE_MAP), "个条目")
print("请根据需要手动应用到 fact_sheet.md")
