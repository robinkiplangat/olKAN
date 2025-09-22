"""
Enumeration types for olKAN v2.0
"""

from enum import Enum


class StorageBackend(str, Enum):
    """Storage backend types"""
    FLAT_FILE = "flat_file"
    DATABASE = "database"
    HYBRID = "hybrid"
    S3 = "s3"


class DatasetStatus(str, Enum):
    """Dataset status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class LicenseType(str, Enum):
    """License type enumeration"""
    MIT = "MIT"
    APACHE_2_0 = "Apache-2.0"
    GPL_3_0 = "GPL-3.0"
    BSD_3_CLAUSE = "BSD-3-Clause"
    CC_BY_4_0 = "CC-BY-4.0"
    CC0_1_0 = "CC0-1.0"
    PROPRIETARY = "proprietary"
    UNKNOWN = "unknown"


class DataFormat(str, Enum):
    """Data format enumeration"""
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    PARQUET = "parquet"
    EXCEL = "excel"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    API = "api"
    OTHER = "other"


class DataCategory(str, Enum):
    """Data category enumeration"""
    RESEARCH = "research"
    BUSINESS = "business"
    GOVERNMENT = "government"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    TECHNOLOGY = "technology"
    ENVIRONMENT = "environment"
    SOCIAL = "social"
    ECONOMIC = "economic"
    DEMOGRAPHIC = "demographic"
    SCIENTIFIC = "scientific"
    OTHER = "other"


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    GUEST = "guest"


class PermissionType(str, Enum):
    """Permission type enumeration"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class LogLevel(str, Enum):
    """Log level enumeration"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class HTTPMethod(str, Enum):
    """HTTP method enumeration"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class SortOrder(str, Enum):
    """Sort order enumeration"""
    ASC = "asc"
    DESC = "desc"


class FilterOperator(str, Enum):
    """Filter operator enumeration"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    IN = "in"
    NOT_IN = "not_in"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class AggregationType(str, Enum):
    """Aggregation type enumeration"""
    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    DISTINCT = "distinct"


class ExportFormat(str, Enum):
    """Export format enumeration"""
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    EXCEL = "excel"
    PDF = "pdf"
    HTML = "html"


class NotificationType(str, Enum):
    """Notification type enumeration"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationChannel(str, Enum):
    """Notification channel enumeration"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class CacheStrategy(str, Enum):
    """Cache strategy enumeration"""
    NO_CACHE = "no_cache"
    CACHE_FIRST = "cache_first"
    NETWORK_FIRST = "network_first"
    CACHE_ONLY = "cache_only"
    NETWORK_ONLY = "network_only"


class CompressionType(str, Enum):
    """Compression type enumeration"""
    NONE = "none"
    GZIP = "gzip"
    DEFLATE = "deflate"
    BROTLI = "brotli"
    LZ4 = "lz4"


class EncryptionType(str, Enum):
    """Encryption type enumeration"""
    NONE = "none"
    AES_256 = "aes_256"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    CHACHA20_POLY1305 = "chacha20_poly1305"


class ValidationStatus(str, Enum):
    """Validation status enumeration"""
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


class ProcessingStatus(str, Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IndexStatus(str, Enum):
    """Index status enumeration"""
    NOT_INDEXED = "not_indexed"
    INDEXING = "indexing"
    INDEXED = "indexed"
    INDEX_FAILED = "index_failed"
    OUTDATED = "outdated"


class SyncStatus(str, Enum):
    """Sync status enumeration"""
    IN_SYNC = "in_sync"
    OUT_OF_SYNC = "out_of_sync"
    SYNCING = "syncing"
    SYNC_FAILED = "sync_failed"


class BackupStatus(str, Enum):
    """Backup status enumeration"""
    NOT_BACKED_UP = "not_backed_up"
    BACKING_UP = "backing_up"
    BACKED_UP = "backed_up"
    BACKUP_FAILED = "backup_failed"


class DeploymentStatus(str, Enum):
    """Deployment status enumeration"""
    NOT_DEPLOYED = "not_deployed"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    DEPLOYMENT_FAILED = "deployment_failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


class HealthStatus(str, Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class MetricType(str, Enum):
    """Metric type enumeration"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(str, Enum):
    """Alert severity enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status enumeration"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"
