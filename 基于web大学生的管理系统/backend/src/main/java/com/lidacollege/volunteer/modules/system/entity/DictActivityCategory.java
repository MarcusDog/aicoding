package com.lidacollege.volunteer.modules.system.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.LocalDateTime;
import lombok.Data;

@Data
@TableName("dict_activity_category")
public class DictActivityCategory {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String categoryCode;
    private String categoryName;
    private Integer sortNo;
    private String categoryStatus;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
