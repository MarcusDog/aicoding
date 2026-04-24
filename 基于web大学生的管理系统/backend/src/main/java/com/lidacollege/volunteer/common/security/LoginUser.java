package com.lidacollege.volunteer.common.security;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class LoginUser {

    private Long userId;
    private String username;
    private String roleCode;
    private Long refId;

    public boolean isAdmin() {
        return "ADMIN".equals(roleCode);
    }

    public boolean isStudent() {
        return "STUDENT".equals(roleCode);
    }
}
