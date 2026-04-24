package com.lidacollege.volunteer.modules.signup.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.LocalDateTime;
import lombok.Data;

@Data
@TableName("activity_signup")
public class ActivitySignup {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long activityId;
    private Long studentId;
    private String signupStatus;
    private String reviewComment;
    private Long reviewedBy;
    private LocalDateTime reviewedAt;
    private String cancelReason;
    private LocalDateTime signupTime;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    @TableLogic
    private Integer isDeleted;
}
