package com.lidacollege.volunteer.modules.sign.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.LocalDateTime;
import lombok.Data;

@Data
@TableName("activity_sign")
public class ActivitySign {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long activityId;
    private Long studentId;
    private String signStatus;
    private LocalDateTime signInTime;
    private LocalDateTime signOutTime;
    private String signInMode;
    private String signOutMode;
    private Long signInOperatorId;
    private Long signOutOperatorId;
    private String exceptionRemark;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
