# Add project specific ProGuard rules here.
-keep class com.ulak.** { *; }
-keepclassmembers class com.ulak.** { *; }

# Coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}

# JSON
-keepclassmembers class * {
    @org.json.** *;
}

# Security
-keep class androidx.security.crypto.** { *; }

# Tink Crypto - Missing annotations and dependencies
-dontwarn javax.annotation.**
-dontwarn javax.annotation.concurrent.**
-dontwarn com.google.api.client.**
-dontwarn org.joda.time.**
-keep class com.google.crypto.tink.** { *; }
