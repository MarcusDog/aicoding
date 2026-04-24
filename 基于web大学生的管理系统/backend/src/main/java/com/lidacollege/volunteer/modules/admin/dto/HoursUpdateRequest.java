package com.lidacollege.volunteer.modules.admin.dto;

import java.math.BigDecimal;

public record HoursUpdateRequest(
    BigDecimal hoursValue,
    String remark
) {
}
