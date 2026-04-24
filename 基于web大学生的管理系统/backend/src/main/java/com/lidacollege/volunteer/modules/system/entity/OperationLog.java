package com.lidacollege.volunteer.modules.system.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.LocalDateTime;
import lombok.Data;

@Data
@TableName("operation_log")
public class OperationLog {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long operatorUserId;
    private String operatorRoleCode;
    private String moduleName;
    private String operationType;
    private Long bizId;
    private String requestPath;
    private String operationDesc;
    private LocalDateTime operationTime;
}
