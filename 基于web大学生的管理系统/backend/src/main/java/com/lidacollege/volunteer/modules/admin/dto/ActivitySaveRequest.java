package com.lidacollege.volunteer.modules.admin.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record ActivitySaveRequest(
    String title,
    String categoryCode,
    String location,
    String organizerName,
    String description,
    String coverUrl,
    String attachmentUrl,
    Integer recruitCount,
    LocalDateTime signupDeadline,
    LocalDateTime startTime,
    LocalDateTime endTime,
    BigDecimal serviceHours
) {
}
