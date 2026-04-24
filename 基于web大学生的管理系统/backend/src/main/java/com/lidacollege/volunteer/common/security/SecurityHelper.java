package com.lidacollege.volunteer.common.security;

import com.lidacollege.volunteer.common.exception.BusinessException;

public final class SecurityHelper {

    private SecurityHelper() {
    }

    public static LoginUser currentUser() {
        return UserContext.get();
    }

    public static void requireAdmin() {
        if (!currentUser().isAdmin()) {
            throw new BusinessException("无管理员权限");
        }
    }

    public static void requireStudent() {
        if (!currentUser().isStudent()) {
            throw new BusinessException("无学生权限");
        }
    }
}
