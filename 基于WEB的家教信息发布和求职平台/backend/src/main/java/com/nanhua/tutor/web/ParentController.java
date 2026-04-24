package com.nanhua.tutor.web;

import com.nanhua.tutor.domain.TutorDemand;
import com.nanhua.tutor.domain.TutorOrder;
import com.nanhua.tutor.service.TutorPlatformService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;
import java.util.List;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@CrossOrigin
@RestController
@RequestMapping("/api/parents")
public class ParentController {
  private final TutorPlatformService service;
  private final ApiViewMapper mapper;

  public ParentController(TutorPlatformService service, ApiViewMapper mapper) {
    this.service = service;
    this.mapper = mapper;
  }

  @PostMapping("/{parentId}/demands")
  DemandView publishDemand(@PathVariable Long parentId, @Valid @RequestBody DemandRequest request) {
    TutorDemand demand = service.publishDemand(
        parentId,
        request.title(),
        request.subject(),
        request.gradeLevel(),
        request.location(),
        request.budgetMin(),
        request.budgetMax(),
        request.schedule(),
        request.description()
    );
    return mapper.demand(demand);
  }

  @PutMapping("/{parentId}/demands/{demandId}")
  DemandView resubmitDemand(@PathVariable Long parentId, @PathVariable Long demandId, @Valid @RequestBody DemandRequest request) {
    TutorDemand demand = service.resubmitDemand(
        parentId,
        demandId,
        request.title(),
        request.subject(),
        request.gradeLevel(),
        request.location(),
        request.budgetMin(),
        request.budgetMax(),
        request.schedule(),
        request.description()
    );
    return mapper.demand(demand);
  }

  @GetMapping("/{parentId}/demands")
  List<DemandView> demands(@PathVariable Long parentId) {
    return service.parentDemands(parentId).stream().map(mapper::demand).toList();
  }

  @GetMapping("/{parentId}/orders")
  List<OrderView> orders(@PathVariable Long parentId) {
    List<TutorOrder> orders = service.parentOrders(parentId);
    return orders.stream().map(mapper::order).toList();
  }

  record DemandRequest(
      @NotBlank String title,
      @NotBlank String subject,
      @NotBlank String gradeLevel,
      @NotBlank String location,
      @NotNull BigDecimal budgetMin,
      @NotNull BigDecimal budgetMax,
      @NotBlank String schedule,
      @NotBlank String description
  ) {
  }
}
