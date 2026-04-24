package com.lidacollege.volunteer.common.api;

import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class PageResponse<T> {

    private Long total;
    private List<T> records;
}
