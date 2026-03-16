# Java 内存模型（JMM）
> 深入理解 JMM 的可见性、原子性与有序性保证，以及 happens-before 规则的实际应用。

## 核心概念 <!-- type: cards -->

Java 内存模型定义了多线程程序中变量的读写规则。

### 可见性
一个线程对共享变量的修改，另一个线程能否及时看到。volatile 关键字可以保证可见性。

### 原子性
操作不可被中断。long/double 的读写在 32 位 JVM 上不是原子的，需要 synchronized 或 AtomicLong。

### 有序性
编译器和处理器会对指令重排序，JMM 通过 happens-before 规则约束可见的重排序。

### happens-before
程序顺序规则、监视器锁规则、volatile 变量规则、线程启动/终止规则。

## 使用流程

1. 确定共享变量
   找出所有被多个线程读写的字段。

2. 选择同步机制
   无竞争读多写少 → volatile；需要复合操作 → synchronized 或 Lock；高并发计数 → Atomic 类。

3. 验证 happens-before 链
   确保写操作 happens-before 读操作，否则存在可见性风险。

4. 压测与分析
   使用 jcstress 或 JCTools 做并发正确性验证。

> [!TIP]
> 优先使用 `java.util.concurrent` 提供的高层并发原语，而非手动管理 volatile + synchronized。

## volatile 示例

```java
public class StopThread {
    private static volatile boolean stopRequested;

    public static void main(String[] args) throws InterruptedException {
        Thread t = new Thread(() -> {
            int i = 0;
            while (!stopRequested) i++;
        });
        t.start();
        TimeUnit.SECONDS.sleep(1);
        stopRequested = true; // visible due to volatile
    }
}
```

```java
// 错误示例：没有 volatile，JVM 可能永远不停止循环
private static boolean stopRequested; // BAD
```

## happens-before 规则对比

| 规则 | 触发条件 | 保证内容 | 常见误区 |
|------|----------|----------|----------|
| 程序顺序规则 | 同一线程内 | 前操作 hb 后操作 | 不跨线程 |
| volatile 写读 | 写 hb 后续读 | 可见性 | 不保证原子性 |
| 监视器解锁/加锁 | unlock hb lock | 可见性 + 互斥 | 需同一锁对象 |
| 线程 start | start() hb 线程体 | 启动前写入可见 | join 才保证终止 |
| 传递性 | A hb B, B hb C | A hb C | 链断则失效 |

## 常见陷阱

<details>
<summary>双重检查锁定（DCL）为什么需要 volatile？</summary>
<div>
对象初始化分三步：分配内存、初始化字段、将引用指向内存。步骤 2 和 3 可能被重排序，导致另一个线程看到未初始化的对象。volatile 禁止这个重排序。
</div>
</details>

<details>
<summary>long/double 非原子性在现代 JVM 上还有影响吗？</summary>
<div>
HotSpot JVM 在 64 位平台上实际保证了 long/double 的原子性，但这不是 JMM 规范要求的行为，依赖具体实现，跨平台代码仍应使用 volatile 或 AtomicLong。
</div>
</details>

## 总结

Java 内存模型通过 happens-before 规则在性能与正确性之间取得平衡。正确理解三大特性（可见性、原子性、有序性）以及各同步机制的语义，是写出正确并发程序的基础。优先使用 `java.util.concurrent`，只在性能热点才考虑 volatile 等底层机制。
