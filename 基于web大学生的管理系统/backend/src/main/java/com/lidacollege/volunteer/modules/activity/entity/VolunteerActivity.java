package com.lidacollege.volunteer.modules.activity.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import lombok.Data;

@Data
@TableName("volunteer_activity")
public class VolunteerActivity {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String title;
    private String categoryCode;
    private String location;
    private String organizerName;
    private String description;
    private String coverUrl;
    private String attachmentUrl;
    private Integer recruitCount;
    private LocalDateTime signupDeadline;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private BigDecimal serviceHours;
    private String checkInCode;
    private String checkOutCode;
    private String activityStatus;
    private Long publishedBy;
    private LocalDateTime publishedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    @TableLogic
    private Integer isDeleted;
}
