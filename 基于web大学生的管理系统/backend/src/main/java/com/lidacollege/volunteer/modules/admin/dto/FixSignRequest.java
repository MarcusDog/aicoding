package com.lidacollege.volunteer.modules.admin.dto;

import java.time.LocalDateTime;

public record FixSignRequest(
    LocalDateTime signInTime,
    LocalDateTime signOutTime,
    String exceptionRemark
) {
}
