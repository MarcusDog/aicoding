package com.lidacollege.volunteer.common.security;

import com.lidacollege.volunteer.common.exception.BusinessException;

public final class UserContext {

    private static final ThreadLocal<LoginUser> HOLDER = new ThreadLocal<>();

    private UserContext() {
    }

    public static void set(LoginUser loginUser) {
        HOLDER.set(loginUser);
    }

    public static LoginUser get() {
        LoginUser loginUser = HOLDER.get();
        if (loginUser == null) {
            throw new BusinessException("未登录或登录已过期");
        }
        return loginUser;
    }

    public static void clear() {
        HOLDER.remove();
    }
}
