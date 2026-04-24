package com.lidacollege.volunteer.modules.system.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.LocalDateTime;
import lombok.Data;

@Data
@TableName("message_notice")
public class MessageNotice {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    private String messageType;
    private String title;
    private String content;
    private String bizType;
    private Long bizId;
    private Integer isRead;
    private LocalDateTime createdAt;
    private LocalDateTime readAt;
}
