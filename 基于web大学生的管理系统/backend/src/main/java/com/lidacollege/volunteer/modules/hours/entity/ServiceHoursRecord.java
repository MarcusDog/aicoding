package com.lidacollege.volunteer.modules.hours.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import lombok.Data;

@Data
@TableName("service_hours_record")
public class ServiceHoursRecord {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long activityId;
    private Long studentId;
    private Long signupId;
    private Long signId;
    private BigDecimal hoursValue;
    private String hoursStatus;
    private LocalDateTime generatedAt;
    private Long confirmedBy;
    private LocalDateTime confirmedAt;
    private String remark;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
