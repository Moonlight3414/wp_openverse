import { deepFreeze } from "#shared/utils/deep-freeze"

describe("deepFreeze", () => {
  it("should freeze shallow arrays", async () => {
    const a = [1, 2]
    deepFreeze(a)
    expect(() => (a[0] = "a")).toThrow()
  })

  it("should freeze shallow objects", async () => {
    const a = { a: 1, b: 2 }
    deepFreeze(a)
    expect(() => (a.a = 5)).toThrow()
  })

  it("should freeze nested arrays", async () => {
    const a = [[2], 5]
    deepFreeze(a)
    expect(() => (a[0][0] = "a")).toThrow()
  })

  it("should freeze nested objects", async () => {
    const a = { a: { b: 2 } }
    deepFreeze(a)
    expect(() => (a.a.b = 5)).toThrow()
  })

  it("should freeze objects inside of an array", async () => {
    const a = [[{ a: "b" }]]
    deepFreeze(a)
    expect(() => (a[0][0].a = "1")).toThrow()
  })

  it("should freeze arrays inside of objects", async () => {
    const a = { b: [1] }
    deepFreeze(a)
    expect(() => a.b.push(3)).toThrow()
  })
})
